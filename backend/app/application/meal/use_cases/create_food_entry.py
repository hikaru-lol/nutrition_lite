from __future__ import annotations

from app.application.meal.dto.food_entry_dto import (
    CreateFoodEntryInputDTO,
    FoodEntryDTO,
)
from app.application.meal.use_cases._helpers import food_entry_to_dto
from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.meal.errors import InvalidMealTypeError
from app.domain.meal.value_objects import FoodEntryId, MealType
from app.application.meal.ports.uow_port import MealUnitOfWorkPort


class CreateFoodEntryUseCase:
    """
    FoodEntry（1品の食事ログ）を新規作成する UseCase。
    """

    def __init__(self, meal_uow: MealUnitOfWorkPort) -> None:
        self._meal_uow = meal_uow

    def execute(self, user_id: UserId, dto: CreateFoodEntryInputDTO) -> FoodEntryDTO:
        try:
            meal_type = MealType(dto.meal_type)
        except ValueError:
            raise InvalidMealTypeError(f"Invalid meal_type: {dto.meal_type}")

        entry = FoodEntry(
            id=FoodEntryId.new(),
            user_id=user_id,
            date=dto.date,
            meal_type=meal_type,
            meal_index=dto.meal_index,
            name=dto.name,
            amount_value=dto.amount_value,
            amount_unit=dto.amount_unit,
            serving_count=dto.serving_count,
            note=dto.note,
            created_at=None,
            updated_at=None,
            deleted_at=None,
        )

        with self._meal_uow as uow:
            uow.food_entry_repo.add(entry)

        return food_entry_to_dto(entry)
