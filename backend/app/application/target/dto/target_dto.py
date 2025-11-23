from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from app.domain.target.entities import TargetDefinition, TargetNutrient
from app.domain.target.value_objects import GoalType, ActivityLevel, NutrientCode


@dataclass
class TargetNutrientDTO:
    """1つの栄養素に対するターゲット値を表す DTO。"""

    code: NutrientCode
    amount: float
    unit: str
    source: str

    @classmethod
    def from_entity(cls, entity: TargetNutrient) -> "TargetNutrientDTO":
        return cls(
            code=entity.code,
            amount=entity.amount.value,
            unit=entity.amount.unit,
            source=entity.source.value,
        )


@dataclass
class TargetDTO:
    """
    ターゲット定義の DTO。

    - アプリケーション層と API 層の間のデータ受け渡しに使用。
    """

    id: str
    user_id: str
    title: str
    goal_type: GoalType
    goal_description: Optional[str]
    activity_level: ActivityLevel
    nutrients: List[TargetNutrientDTO]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    llm_rationale: Optional[str]
    disclaimer: Optional[str]

    @classmethod
    def from_entity(cls, entity: TargetDefinition) -> "TargetDTO":
        return cls(
            id=entity.id.value,
            user_id=entity.user_id.value,
            title=entity.title,
            goal_type=entity.goal_type,
            goal_description=entity.goal_description,
            activity_level=entity.activity_level,
            nutrients=[TargetNutrientDTO.from_entity(
                n) for n in entity.nutrients],
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            llm_rationale=entity.llm_rationale,
            disclaimer=entity.disclaimer,
        )


@dataclass
class CreateTargetInputDTO:
    """
    新しいターゲットを作成する際の入力 DTO。

    - 栄養素の具体的な値は TargetGeneratorPort で決定する。
    """

    user_id: str
    title: str
    goal_type: GoalType
    goal_description: Optional[str]
    activity_level: ActivityLevel


@dataclass
class ActivateTargetInputDTO:
    """
    指定ターゲットをアクティブ化する際の入力 DTO。
    """

    user_id: str
    target_id: str

# --- GetTarget 用 ------------------------------------------------------


@dataclass(slots=True)
class GetTargetInputDTO:
    """1件取得用の入力 DTO（認証済みユーザーの target_id ）"""

    user_id: str
    target_id: str


# --- UpdateTarget 用 ---------------------------------------------------


@dataclass(slots=True)
class UpdateTargetNutrientDTO:
    """栄養素1つ分のパッチ情報"""

    code: str
    amount: Optional[float] = None
    unit: Optional[str] = None
    # source は UC 側で "manual" に変更するので、ここからは受け取らない


@dataclass(slots=True)
class UpdateTargetInputDTO:
    """
    Target の部分更新用 DTO。

    - None のフィールドは「その項目は更新しない」
    - 値が入っているフィールドだけを更新する（PATCH 的な挙動）
    """

    user_id: str
    target_id: str

    title: Optional[str] = None
    goal_type: Optional[str] = None
    goal_description: Optional[str] = None
    activity_level: Optional[str] = None

    llm_rationale: Optional[str] = None
    disclaimer: Optional[str] = None

    nutrients: Optional[list[UpdateTargetNutrientDTO]] = None
