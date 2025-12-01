from __future__ import annotations

from datetime import datetime
from uuid import UUID
from typing import Literal

from pydantic import BaseModel

from app.application.target.dto.target_dto import TargetDTO
from app.domain.target.value_objects import NutrientSourceLiteral


# === Literal 型定義 =========================================================

# Auth の UserPlanLiteral と同じノリで Literal 型を用意
GoalTypeLiteral = Literal[
    "weight_loss",   # 減量
    "maintain",      # 体重維持
    "weight_gain",   # 増量
    "health_improve"  # 健康改善
]

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


# === Response Schemas =======================================================


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
    goal_description: str | None
    activity_level: ActivityLevelLiteral

    is_active: bool

    nutrients: list[TargetNutrientSchema]

    llm_rationale: str | None
    disclaimer: str | None

    created_at: datetime
    updated_at: datetime


class TargetListResponse(BaseModel):
    """
    ターゲット一覧レスポンス。
    """

    items: list[TargetResponse]


# === Request Schemas ========================================================


class CreateTargetRequest(BaseModel):
    """
    ターゲット作成用リクエスト。

    17栄養素の中身はサーバ側で生成する。
    """

    title: str
    goal_type: GoalTypeLiteral
    goal_description: str | None = None
    activity_level: ActivityLevelLiteral


class UpdateTargetNutrientSchema(BaseModel):
    """
    ターゲット内の特定栄養素の部分更新用。
    """

    # TODO: バリデーションを厳しくするなら NutrientCodeLiteral に戻してもよい
    code: str
    amount: float | None = None
    unit: str | None = None


class UpdateTargetRequest(BaseModel):
    """
    ターゲットの部分更新（PATCH）的なリクエスト。

    - None / 未指定のフィールドは更新しない。
    """

    title: str | None = None
    goal_type: GoalTypeLiteral | None = None
    goal_description: str | None = None
    activity_level: ActivityLevelLiteral | None = None
    llm_rationale: str | None = None
    disclaimer: str | None = None
    nutrients: list[UpdateTargetNutrientSchema] | None = None

    class Config:
        extra = "forbid"  # 余計なフィールドは受け取らない


# === DTO -> Schema 変換ヘルパー ============================================


def target_dto_to_schema(dto: TargetDTO) -> TargetResponse:
    """
    TargetDTO -> TargetResponse への変換。
    """
    nutrients = [
        TargetNutrientSchema(
            code=nut.code,          # str -> NutrientCodeLiteral（Pydantic が変換 / バリデーション）
            amount=nut.amount,
            unit=nut.unit,
            source=nut.source,      # str -> NutrientSourceLiteral
        )
        for nut in dto.nutrients
    ]

    return TargetResponse(
        id=dto.id,                  # str -> UUID（Pydantic が変換）
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


def target_list_dto_to_schema(dtos: list[TargetDTO]) -> TargetListResponse:
    """
    TargetDTO のリスト -> TargetListResponse への変換。
    """
    return TargetListResponse(
        items=[target_dto_to_schema(dto) for dto in dtos]
    )
