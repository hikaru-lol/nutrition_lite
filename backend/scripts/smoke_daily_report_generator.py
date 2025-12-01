from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date as DateType
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from app.application.nutrition.dto.daily_report_llm_dto import (
    DailyReportLLMInput,
    DailyReportLLMOutput,
)
from app.domain.auth.value_objects import UserId
from app.domain.target.value_objects import (
    NutrientAmount,
    NutrientCode,
    NutrientSource,
)
from app.infra.llm.stub_daily_report_generator import (
    StubDailyNutritionReportGenerator,
)
from app.infra.llm.daily_report_generator_openai import (
    OpenAIDailyNutritionReportGenerator,
    OpenAIDailyReportGeneratorConfig,
)

# DailyReportGenerationFailedError がまだ無ければ、必要に応じて path を調整してください
try:
    from app.application.nutrition.errors import DailyReportGenerationFailedError
except ImportError:  # フォールバック（未定義ならとりあえず Exception 扱い）
    DailyReportGenerationFailedError = Exception  # type: ignore[misc]

# プロジェクトルート（backend/）を基準に .env を読む
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _env_bool(name: str, default: bool = False) -> bool:
    """環境変数を boolean として扱う小ヘルパー。"""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in ("1", "true", "yes", "on")


# === スタブ用の簡易ドメインオブジェクト ================================

@dataclass
class ProfileStub:
    sex: str | None
    birthdate: DateType | None
    height_cm: float | None
    weight_kg: float | None
    meals_per_day: int | None


@dataclass
class TargetSnapshotStub:
    goal_type: str
    activity_level: str


@dataclass
class NutrientStub:
    code: NutrientCode
    amount: NutrientAmount
    source: NutrientSource


@dataclass
class DailySummaryStub:
    nutrients: list[NutrientStub]


@dataclass
class MealSummaryStub:
    date: DateType
    meal_type: str
    nutrients: list[NutrientStub]


def build_sample_input() -> DailyReportLLMInput:
    """
    テスト用の DailyReportLLMInput を作る。

    - 実際の Profile / DailyTargetSnapshot / DailyNutritionSummary / MealNutritionSummary
      を使う代わりに、ここでは最小限のスタブを使っている。
    """
    user_id = UserId("smoke-user-daily-report")
    target_date = DateType.today()

    profile = ProfileStub(
        sex="male",
        birthdate=DateType(1990, 1, 1),
        height_cm=175.0,
        weight_kg=70.0,
        meals_per_day=3,
    )

    target_snapshot = TargetSnapshotStub(
        goal_type="weight_loss",
        activity_level="normal",
    )

    # ざっくり適当な日次栄養サマリ
    daily_nutrients: list[NutrientStub] = [
        NutrientStub(
            code=NutrientCode.CARBOHYDRATE,
            amount=NutrientAmount(value=250.0, unit="g"),
            source=NutrientSource("llm"),
        ),
        NutrientStub(
            code=NutrientCode.PROTEIN,
            amount=NutrientAmount(value=80.0, unit="g"),
            source=NutrientSource("llm"),
        ),
        NutrientStub(
            code=NutrientCode.FAT,
            amount=NutrientAmount(value=60.0, unit="g"),
            source=NutrientSource("llm"),
        ),
    ]
    daily_summary = DailySummaryStub(nutrients=daily_nutrients)

    # Meal summary は2食分くらい用意
    meal_summaries: list[MealSummaryStub] = [
        MealSummaryStub(
            date=target_date,
            meal_type="breakfast",
            nutrients=daily_nutrients[:2],
        ),
        MealSummaryStub(
            date=target_date,
            meal_type="dinner",
            nutrients=daily_nutrients[1:],
        ),
    ]

    return DailyReportLLMInput(
        user_id=user_id,
        date=target_date,
        profile=profile,
        target_snapshot=target_snapshot,
        daily_summary=daily_summary,
        meal_summaries=meal_summaries,
    )


def build_generator():
    """
    環境変数を見て Stub / OpenAI どちらの DailyReportGenerator を使うか決める。
    """
    api_key = os.getenv("OPENAI_API_KEY")
    use_llm = _env_bool("USE_OPENAI_DAILY_REPORT_GENERATOR", False)

    print("USE_OPENAI_DAILY_REPORT_GENERATOR =", use_llm)
    print(
        "OPENAI_API_KEY prefix =",
        api_key[:8] + "..." if api_key else "None",
    )

    # フラグが false なら強制的に stub
    if not use_llm:
        print(
            "-> USE_OPENAI_DAILY_REPORT_GENERATOR = False のため StubDailyNutritionReportGenerator を使用します。"
        )
        return StubDailyNutritionReportGenerator()

    # フラグは true でもキーが無ければ stub にフォールバック
    if not api_key:
        print(
            "-> OPENAI_API_KEY が設定されていないため StubDailyNutritionReportGenerator を使用します。"
        )
        return StubDailyNutritionReportGenerator()

    # モデル名や温度も env から読みつつ、デフォルト値を用意
    model = os.getenv("OPENAI_DAILY_REPORT_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("OPENAI_DAILY_REPORT_TEMPERATURE", "0.4"))

    # OpenAI クライアント（env から API キーを読む）
    client = OpenAI()
    print(
        f"-> OpenAI DailyReportGenerator model={model}, temperature={temperature} で実行します。"
    )

    return OpenAIDailyNutritionReportGenerator(
        client=client,
        config=OpenAIDailyReportGeneratorConfig(
            model=model,
            temperature=temperature,
        ),
    )


def main() -> None:
    generator = build_generator()
    llm_input = build_sample_input()

    print("=== Smoke test for DailyNutritionReportGenerator ===")
    print(f"user_id = {llm_input.user_id.value}")
    print(f"date    = {llm_input.date.isoformat()}")
    print()

    try:
        output: DailyReportLLMOutput = generator.generate(llm_input)
    except DailyReportGenerationFailedError as e:
        print("[ERROR] Daily report generation failed:", e)
        return

    print("=== LLM Output ===")
    print("\n[SUMMARY]")
    print(output.summary)

    print("\n[GOOD POINTS]")
    for idx, item in enumerate(output.good_points, start=1):
        print(f"{idx}. {item}")

    print("\n[IMPROVEMENT POINTS]")
    for idx, item in enumerate(output.improvement_points, start=1):
        print(f"{idx}. {item}")

    print("\n[TOMORROW FOCUS]")
    for idx, item in enumerate(output.tomorrow_focus, start=1):
        print(f"{idx}. {item}")


if __name__ == "__main__":
    main()
