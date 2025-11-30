# app/application/nutrition/ports/nutrition_estimator_port.py

from __future__ import annotations

from datetime import date as DateType
from typing import Protocol, Sequence

from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.application.nutrition.dto.meal_nutrient_intake_dto import MealNutrientIntake


class NutritionEstimatorPort(Protocol):
    """
    Meal 単位の栄養素を推定するためのポート。

    - FoodEntry の集合を受け取り、MealNutrientIntake のリストを返す。
    - 具体実装は LLM / ルールベース / 外部 DB など何でもよい。
    """

    def estimate_for_entries(
        self,
        user_id: UserId,
        date: DateType,
        entries: Sequence[FoodEntry],
    ) -> list[MealNutrientIntake]:
        ...
