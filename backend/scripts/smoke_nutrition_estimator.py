# backend/scripts/smoke_nutrition_estimator.py
from __future__ import annotations

import os
from datetime import date as DateType
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.meal.value_objects import FoodEntryId, MealType
from app.domain.nutrition.errors import NutritionEstimationFailedError
from app.infra.nutrition.estimator_stub import StubNutritionEstimator
from app.infra.llm.estimator_openai import (
    OpenAINutritionEstimator,
    OpenAINutritionEstimatorConfig,
)


# プロジェクトルート（backend/）を基準に .env を読む
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _env_bool(name: str, default: bool = False) -> bool:
    """環境変数を boolean として扱う小ヘルパー。"""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in ("1", "true", "yes", "on")


def build_sample_entries(user_id: UserId, target_date: DateType) -> list[FoodEntry]:
    """
    テスト用の FoodEntry をいくつか作成する。

    - 和食っぽい例: ご飯 + 味噌汁 + 焼き鮭
    """
    entries: list[FoodEntry] = []

    entries.append(
        FoodEntry(
            id=FoodEntryId.new(),
            user_id=user_id,
            date=target_date,
            meal_type=MealType.MAIN,
            meal_index=1,
            name="白ごはん",
            amount_value=200.0,
            amount_unit="g",
            serving_count=1,
            note="茶碗1杯分のご飯",
            created_at=None,
            updated_at=None,
            deleted_at=None,
        )
    )

    entries.append(
        FoodEntry(
            id=FoodEntryId.new(),
            user_id=user_id,
            date=target_date,
            meal_type=MealType.MAIN,
            meal_index=1,
            name="味噌汁",
            amount_value=1.0,
            amount_unit="杯",
            serving_count=1,
            note="豆腐とわかめの味噌汁",
            created_at=None,
            updated_at=None,
            deleted_at=None,
        )
    )

    entries.append(
        FoodEntry(
            id=FoodEntryId.new(),
            user_id=user_id,
            date=target_date,
            meal_type=MealType.MAIN,
            meal_index=1,
            name="焼き鮭",
            amount_value=100.0,
            amount_unit="g",
            serving_count=1,
            note="塩鮭1切れ",
            created_at=None,
            updated_at=None,
            deleted_at=None,
        )
    )

    return entries


def build_estimator():
    """
    環境変数を見て Stub / OpenAI どちらの Estimator を使うか決める。
    """
    api_key = os.getenv("OPENAI_API_KEY")
    use_llm = _env_bool("USE_OPENAI_NUTRITION_ESTIMATOR", False)

    print("USE_OPENAI_NUTRITION_ESTIMATOR =", use_llm)
    print(
        "OPENAI_API_KEY prefix =",
        api_key[:8] + "..." if api_key else "None",
    )

    # フラグが false なら強制的に stub
    if not use_llm:
        print(
            "-> USE_OPENAI_NUTRITION_ESTIMATOR = False のため StubNutritionEstimator を使用します。")
        return StubNutritionEstimator()

    # フラグは true でもキーが無ければ stub にフォールバック
    if not api_key:
        print("-> OPENAI_API_KEY が設定されていないため StubNutritionEstimator を使用します。")
        return StubNutritionEstimator()

    # モデル名や温度も env から読みつつ、デフォルト値を用意
    model = os.getenv("OPENAI_NUTRITION_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("OPENAI_NUTRITION_TEMPERATURE", "0.1"))

    # OpenAI クライアント（env から API キーを読む）
    client = OpenAI()
    print(
        f"-> OpenAI Nutrition Estimator model={model}, temperature={temperature} で実行します。")

    return OpenAINutritionEstimator(
        client=client,
        config=OpenAINutritionEstimatorConfig(
            model=model,
            temperature=temperature,
        ),
    )


def main() -> None:
    # テスト用のユーザーID & 日付
    user_id = UserId("test-user-for-nutrition-estimator")
    target_date = DateType.today()

    estimator = build_estimator()
    entries = build_sample_entries(user_id, target_date)

    print("=== Smoke test for NutritionEstimator ===")
    print(f"user_id = {user_id.value}")
    print(f"date    = {target_date.isoformat()}")
    print(f"entries = {len(entries)} items")
    for e in entries:
        print(f"- {e.name} ({e.amount_value} {e.amount_unit})")

    print("\nEstimating nutrients...\n")

    try:
        nutrients = estimator.estimate_for_entries(
            user_id=user_id,
            date=target_date,
            entries=entries,
        )
    except NutritionEstimationFailedError as e:
        print("[ERROR] Nutrition estimation failed:", e)
        return

    print("Result nutrients:")
    for n in nutrients:
        # MealNutrientIntake(code: NutrientCode, amount: NutrientAmount, source: NutrientSource)
        code = getattr(n.code, "value", n.code)
        source = getattr(n.source, "value", n.source)
        print(
            f"- {code:14s} : {n.amount.value:.2f} {n.amount.unit} "
            f"(source={source})"
        )


if __name__ == "__main__":
    main()
