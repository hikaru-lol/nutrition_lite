from __future__ import annotations

from app.application.meal.dto.food_entry_dto import (
    CreateFoodEntryInputDTO,
    FoodEntryDTO,
)
from app.application.meal.ports.food_entry_repository_port import (
    FoodEntryRepositoryPort,
)
from app.application.meal.use_cases._helpers import food_entry_to_dto
from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.meal.errors import InvalidMealTypeError
from app.domain.meal.value_objects import FoodEntryId, MealType


class CreateFoodEntryUseCase:
    """
    FoodEntry（1品の食事ログ）を新規作成する UseCase。
    """

    def __init__(self, repo: FoodEntryRepositoryPort) -> None:
        self._repo = repo

    def execute(self, user_id: UserId, dto: CreateFoodEntryInputDTO) -> FoodEntryDTO:
        # meal_type の文字列 -> Enum 変換
        try:
            meal_type = MealType(dto.meal_type)
        except ValueError:
            raise InvalidMealTypeError(f"Invalid meal_type: {dto.meal_type}")

        # created_at / updated_at は None のまま渡し、Repo/DB 側で埋める方針
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
        # __post_init__ 内で meal_index / amount のバリデーション

        self._repo.add(entry)

        return food_entry_to_dto(entry)
