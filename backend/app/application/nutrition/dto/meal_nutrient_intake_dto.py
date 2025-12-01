from __future__ import annotations
from dataclasses import dataclass

from app.domain.target.value_objects import NutrientCode, NutrientAmount, NutrientSource


@dataclass(slots=True)
class MealNutrientIntake:
    code: NutrientCode
    amount: NutrientAmount
    source: NutrientSource
