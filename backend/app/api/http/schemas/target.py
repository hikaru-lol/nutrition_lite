from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal
from uuid import UUID

from pydantic import BaseModel

from app.application.target.dto.target_dto import TargetDTO, TargetNutrientDTO
from app.domain.target.value_objects import NutrientSourceLiteral

# Auth の UserPlanLiteral と同じノリで Literal 型を用意
GoalTypeLiteral = Literal["weight_loss",
                          "maintain", "weight_gain", "health_improve"]
ActivityLevelLiteral = Literal["low", "normal", "high"]

NutrientCodeLiteral = Literal[
    # エネルギー源
    "carbohydrate",
    "fat",
    "protein",
    # ビタミン
    "vitamin_a",
    "vitamin_b_complex",
    "vitamin_c",
    "vitamin_d",
    "vitamin_e",
    "vitamin_k",
    # ミネラル
    "calcium",
    "iron",
    "magnesium",
    "zinc",
    "sodium",
    "potassium",
    # その他
    "fiber",
    "water",
]


class TargetNutrientSchema(BaseModel):
    """
    1つの栄養素に対するターゲット値（API用スキーマ）。
    """

    code: NutrientCodeLiteral
    amount: float
    unit: str
    source: NutrientSourceLiteral  # "llm" / "manual" / "user_input"


class TargetResponse(BaseModel):
    """
    1つのターゲット定義のレスポンス。
    """

    id: UUID
    user_id: UUID

    title: str
    goal_type: GoalTypeLiteral
    goal_description: Optional[str]
    activity_level: ActivityLevelLiteral

    is_active: bool

    nutrients: List[TargetNutrientSchema]

    llm_rationale: Optional[str]
    disclaimer: Optional[str]

    created_at: datetime
    updated_at: datetime


class TargetListResponse(BaseModel):
    """
    ターゲット一覧レスポンス。
    """

    items: List[TargetResponse]


# ---------------------------------------------------------------------
# リクエスト用スキーマ
# ---------------------------------------------------------------------


class CreateTargetRequest(BaseModel):
    """
    ターゲット作成用リクエスト。

    17栄養素の中身はサーバ側で生成する。
    """

    title: str
    goal_type: GoalTypeLiteral
    goal_description: Optional[str] = None
    activity_level: ActivityLevelLiteral


class UpdateTargetNutrientSchema(BaseModel):
    """
    ターゲット内の特定栄養素の部分更新用。
    """

    # code: NutrientCodeLiteral
    code: str
    amount: Optional[float] = None
    unit: Optional[str] = None


class UpdateTargetRequest(BaseModel):
    """
    ターゲットの部分更新（PATCH）的なリクエスト。

    - None / 未指定のフィールドは更新しない。
    """

    title: Optional[str] = None
    goal_type: Optional[GoalTypeLiteral] = None
    goal_description: Optional[str] = None
    activity_level: Optional[ActivityLevelLiteral] = None
    llm_rationale: Optional[str] = None
    disclaimer: Optional[str] = None
    nutrients: Optional[List[UpdateTargetNutrientSchema]] = None

    class Config:
        extra = "forbid"  # 余計なフィールドは受け取らない


# ---------------------------------------------------------------------
# DTO -> Schema 変換ヘルパー
# ---------------------------------------------------------------------


def target_dto_to_schema(dto: TargetDTO) -> TargetResponse:
    """
    TargetDTO -> TargetResponse への変換。
    """
    nutrients = [
        TargetNutrientSchema(
            code=nut.code,          # str -> NutrientCodeLiteral
            amount=nut.amount,
            unit=nut.unit,
            source=nut.source,      # str -> NutrientSourceLiteral
        )
        for nut in dto.nutrients
    ]

    return TargetResponse(
        id=dto.id,                  # str -> UUID
        user_id=dto.user_id,
        title=dto.title,
        goal_type=dto.goal_type,    # str -> GoalTypeLiteral
        goal_description=dto.goal_description,
        activity_level=dto.activity_level,  # str -> ActivityLevelLiteral
        is_active=dto.is_active,
        nutrients=nutrients,
        llm_rationale=dto.llm_rationale,
        disclaimer=dto.disclaimer,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


def target_list_dto_to_schema(dtos: List[TargetDTO]) -> TargetListResponse:
    return TargetListResponse(
        items=[target_dto_to_schema(dto) for dto in dtos]
    )
