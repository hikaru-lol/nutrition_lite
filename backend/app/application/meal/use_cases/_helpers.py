from __future__ import annotations

from app.application.meal.dto.food_entry_dto import FoodEntryDTO
from app.domain.meal.entities import FoodEntry


def food_entry_to_dto(entry: FoodEntry) -> FoodEntryDTO:
    return FoodEntryDTO(
        id=str(entry.id.value),
        date=entry.date,
        meal_type=entry.meal_type.value,
        meal_index=entry.meal_index,
        name=entry.name,
        amount_value=entry.amount_value,
        amount_unit=entry.amount_unit,
        serving_count=entry.serving_count,
        note=entry.note,
    )
