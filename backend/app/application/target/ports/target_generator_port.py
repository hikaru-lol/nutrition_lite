from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol, runtime_checkable

from app.domain.auth.value_objects import UserId
from app.domain.target.entities import TargetNutrient
from app.domain.target.value_objects import GoalType, ActivityLevel


@dataclass(slots=True)
class TargetGenerationContext:
    """
    ターゲット生成のための入力情報。

    - Profile ドメインから必要な情報を詰め替えて渡す想定。
    - あくまで Application 層の DTO なので、必要に応じて項目を追加してOK。
    """

    user_id: UserId

    # プロフィール系
    sex: str | None          # "male" / "female" / "other" 等、細かい enum は Profile 側に委ねる
    birthdate: date | None
    height_cm: float | None
    weight_kg: float | None

    # 目標系
    goal_type: GoalType
    activity_level: ActivityLevel

    # 将来、睡眠・ストレス・既往歴などを追加してもよい


@dataclass(slots=True)
class TargetGenerationResult:
    """
    ターゲット生成の結果。

    - TargetDefinition を作るために必要な「10栄養素 + 説明文」をまとめたもの。
    """

    nutrients: list[TargetNutrient]
    llm_rationale: str | None = None
    disclaimer: str | None = None


@runtime_checkable
class TargetGeneratorPort(Protocol):
    """
    プロフィール情報 + 目標情報からターゲット栄養素セットを生成するポート。

    - 開発中は Stub 実装（一定のロジックで固定値を返す）
    - 本番では OpenAI などの LLM 実装に差し替える
    - 戻り値の `list[TargetNutrient]` は、必ず
      ALL_NUTRIENT_CODES（carbohydrate, fat, protein, water, fiber, sodium,
      iron, calcium, vitamin_d, potassium）のみをコードとして含むこと。
    """

    def generate(self, ctx: TargetGenerationContext) -> TargetGenerationResult:
        """
        ターゲット生成を行い、10栄養素 + 説明文を返す。
        """
        ...
