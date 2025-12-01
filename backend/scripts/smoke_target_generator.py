# backend/scripts/smoke_target_generator.py
from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from dataclasses import asdict, is_dataclass
from pprint import pprint

from dotenv import load_dotenv
from openai import OpenAI

from app.application.target.errors import TargetGenerationFailedError
from app.application.target.ports.target_generator_port import (
    TargetGenerationContext,
    TargetGenerationResult,
)
from app.domain.auth.value_objects import UserId
from app.domain.target.value_objects import GoalType, ActivityLevel
from app.infra.llm.target_generator_stub import StubTargetGenerator
from app.infra.llm.target_generator_openai import (
    OpenAITargetGenerator,
    OpenAITargetGeneratorConfig,
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


def make_ctx() -> TargetGenerationContext:
    """
    テスト用の TargetGenerationContext を適当に1つ作る。

    本番では CreateTargetUseCase から渡されるのと同じ形。
    """
    return TargetGenerationContext(
        user_id=UserId("smoke-user"),
        sex="male",
        birthdate=date(1990, 1, 1),
        height_cm=175.0,
        weight_kg=70.0,
        goal_type=GoalType.WEIGHT_LOSS,
        activity_level=ActivityLevel.NORMAL,
    )


def build_generator():
    """
    環境変数を見て Stub / OpenAI どちらのジェネレーターを使うか決める。
    """
    api_key = os.getenv("OPENAI_API_KEY")
    use_llm = _env_bool("USE_OPENAI_TARGET_GENERATOR", False)

    print("USE_OPENAI_TARGET_GENERATOR =", use_llm)
    print(
        "OPENAI_API_KEY prefix =",
        api_key[:8] + "..." if api_key else "None",
    )

    # フラグが false なら強制的に stub
    if not use_llm:
        print("-> USE_OPENAI_TARGET_GENERATOR = False のため StubTargetGenerator を使用します。")
        return StubTargetGenerator()

    # フラグは true でもキーが無ければ stub にフォールバック
    if not api_key:
        print("-> OPENAI_API_KEY が設定されていないため StubTargetGenerator を使用します。")
        return StubTargetGenerator()

    # モデル名や温度も env から読みつつ、デフォルト値を用意
    model = os.getenv("OPENAI_TARGET_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("OPENAI_TARGET_TEMPERATURE", "0.2"))

    # OpenAI クライアント（env から API キーを読む）
    client = OpenAI()
    print(f"-> OpenAI model={model}, temperature={temperature} で実行します。")

    return OpenAITargetGenerator(
        client=client,
        config=OpenAITargetGeneratorConfig(
            model=model,
            temperature=temperature,
        ),
    )


def inspect_result(result: TargetGenerationResult) -> None:
    """
    TargetGenerationResult / TargetNutrient の中身を 1 つ 1 つ取り出して表示する。
    """
    print("\n=== TargetGenerationResult ===")
    print("type:", type(result))

    # dataclass であれば asdict で全体像も確認
    if is_dataclass(result):
        print("\n--- asdict(result) ---")
        pprint(asdict(result))

    print("\n--- Top-level fields ---")
    print("nutrients count:", len(result.nutrients))
    print("llm_rationale:", repr(result.llm_rationale))
    print("disclaimer   :", repr(result.disclaimer))

    print("\n--- Each nutrient ---")
    for idx, n in enumerate(result.nutrients, start=1):
        # Enum / VO の .value を持っていれば使う、無ければそのまま
        code = getattr(n.code, "value", n.code)
        source = getattr(n.source, "value", n.source)

        print(f"[{idx:02d}] code={code}")
        print(f"      amount.value={n.amount.value}")
        print(f"      amount.unit ={n.amount.unit}")
        print(f"      source      ={source}")


def main() -> None:
    generator = build_generator()
    ctx = make_ctx()

    try:
        result = generator.generate(ctx)
    except TargetGenerationFailedError as e:
        print("[ERROR] Target generation failed:", e)
        return

    # 中身を 1 つ 1 つ取り出して確認
    inspect_result(result)


if __name__ == "__main__":
    main()
