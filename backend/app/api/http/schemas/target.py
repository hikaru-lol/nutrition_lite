from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.domain.target.value_objects import (
    GoalType,
    ActivityLevel,
    NutrientCode,
)


class TargetCreateRequest(BaseModel):
    """
    ターゲット作成時のリクエスト。

    - Profile に登録されている sex / birthdate / height_cm / weight_kg に加え、
      以下の情報を受け取り、モデル（LLM 等）で 17 栄養素の目標値を生成する。
    """

    title: str
    goal_type: GoalType
    goal_description: Optional[str] = None
    activity_level: ActivityLevel


class TargetNutrientUpdate(BaseModel):
    """
    ターゲット更新時に個別の栄養素を上書きするための入力用スキーマ。
    """

    code: NutrientCode
    amount: float
    unit: str


class TargetUpdateRequest(BaseModel):
    """
    既存ターゲット更新用のリクエスト。

    - すべてのフィールドは任意。
    - nutrients を指定した場合、指定された code の栄養素について amount/unit を上書きし、
      source を "manual" にする想定。
    """

    title: Optional[str] = None
    goal_type: Optional[GoalType] = None
    goal_description: Optional[str] = None
    activity_level: Optional[ActivityLevel] = None
    nutrients: Optional[List[TargetNutrientUpdate]] = None


class TargetNutrient(BaseModel):
    code: NutrientCode
    amount: float
    unit: str
    source: str


class Target(BaseModel):
    id: str
    user_id: str
    title: str
    goal_type: GoalType
    goal_description: Optional[str] = None
    activity_level: ActivityLevel
    is_active: bool
    nutrients: List[TargetNutrient]
    ll_message: Optional[str] = None
    disclaimer: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TargetResponse(BaseModel):
    target: Target


class TargetsResponse(BaseModel):
    items: List[Target]
