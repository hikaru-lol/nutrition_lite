from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MealType(str, Enum):
    """
    食事の種別。

    - main: メインの食事（1回目/2回目/...）
    - snack: 間食
    """
    MAIN = "main"
    SNACK = "snack"


class MealItemRequest(BaseModel):
    """
    FoodEntry 作成・更新用のリクエストスキーマ。

    - date: 対象日
    - meal_type: main / snack
    - meal_index:
        - main のとき: 1..meals_per_day
        - snack のとき: null
    - 量指定:
        - amount_value + amount_unit
        - もしくは serving_count
      のどちらか（または両方）を指定する。
      詳細な整合性チェックはドメイン側（FoodEntry.__post_init__）で行う。
    """

    date: date = Field(..., description="対象日 (YYYY-MM-DD)")
    meal_type: MealType = Field(..., description='"main" または "snack"')
    meal_index: Optional[int] = Field(
        default=None,
        description=(
            "meal_type == main のとき: 1..meals_per_day の整数。"
            "meal_type == snack のとき: null。"
        ),
    )

    name: str = Field(..., description="食品名 / メニュー名")

    amount_value: Optional[float] = Field(
        default=None,
        description="量の実数値。例: 150 (g), 200 (ml) など。",
    )
    amount_unit: Optional[str] = Field(
        default=None,
        description='量の単位。例: "g", "ml", "個", "杯" など。',
    )
    serving_count: Optional[float] = Field(
        default=None,
        description="人前の指定。例: 0.5, 1, 2 など。",
    )

    note: Optional[str] = Field(default=None, description="メモ（任意）")


class MealItemResponse(MealItemRequest):
    """
    FoodEntry 1件分のレスポンススキーマ。
    """

    id: str = Field(..., description="FoodEntry ID (UUID 文字列)")


class MealItemListResponse(BaseModel):
    """
    指定日の FoodEntry 一覧レスポンス。
    """

    items: list[MealItemResponse] = Field(..., description="FoodEntry の配列")
