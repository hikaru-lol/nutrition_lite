from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class NutrientCode(str, Enum):
    # Target の NutrientCode と揃える（必要に応じて import に切り替えてもOK）
    CARBOHYDRATE = "carbohydrate"
    FAT = "fat"
    PROTEIN = "protein"
    VITAMIN_A = "vitamin_a"
    VITAMIN_B_COMPLEX = "vitamin_b_complex"
    VITAMIN_C = "vitamin_c"
    VITAMIN_D = "vitamin_d"
    VITAMIN_E = "vitamin_e"
    VITAMIN_K = "vitamin_k"
    CALCIUM = "calcium"
    IRON = "iron"
    MAGNESIUM = "magnesium"
    ZINC = "zinc"
    SODIUM = "sodium"
    POTASSIUM = "potassium"
    FIBER = "fiber"
    WATER = "water"


class MealType(str, Enum):
    MAIN = "main"
    SNACK = "snack"


class MealNutrientResponse(BaseModel):
    code: NutrientCode = Field(..., description="栄養素コード")
    value: float = Field(..., description="摂取量")
    unit: str = Field(..., description='単位 (例: "g", "mg", "kcal")')
    source: str = Field(...,
                        description='由来 (例: "llm", "manual", "user_input")')


class MealNutritionSummaryResponse(BaseModel):
    id: str = Field(..., description="MealNutritionSummary ID (UUID 文字列)")
    date: date = Field(..., description="対象日 (YYYY-MM-DD)")
    meal_type: MealType = Field(..., description='"main" または "snack"')
    meal_index: Optional[int] = Field(
        default=None,
        description="main のとき: 1..N / snack のとき: null",
    )
    generated_at: datetime = Field(..., description="このサマリを計算した日時")
    nutrients: list[MealNutrientResponse] = Field(
        ..., description="この食事で摂取した栄養素ごとの一覧"
    )


class DailyNutrientResponse(BaseModel):
    """
    1日分の中の、ある1栄養素のレスポンス表現。
    """

    code: str = Field(..., description="栄養素コード (例: protein, fat, vitamin_c)")
    value: float = Field(..., description="1日分の摂取量の合計")
    unit: str = Field(..., description='単位 (例: "g", "mg", "kcal")')
    source: str = Field(
        ..., description='由来 (例: "llm", "manual", "user_input")'
    )


class DailyNutritionSummaryResponse(BaseModel):
    """
    1日分の栄養サマリのレスポンス。
    """

    id: str = Field(..., description="DailyNutritionSummary ID (UUID 文字列)")
    date: date = Field(..., description="対象日 (YYYY-MM-DD)")
    generated_at: datetime = Field(..., description="このサマリを計算した日時")
    nutrients: list[DailyNutrientResponse] = Field(
        ..., description="1日分の栄養素ごとの合計一覧"
    )


class MealAndDailyNutritionResponse(BaseModel):
    """
    Meal + Daily をまとめて返すためのレスポンス。
    """

    meal: MealNutritionSummaryResponse
    daily: DailyNutritionSummaryResponse
