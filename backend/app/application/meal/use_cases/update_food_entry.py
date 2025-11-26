from __future__ import annotations

from uuid import UUID

from app.application.meal.dto.food_entry_dto import (
    UpdateFoodEntryInputDTO,
    UpdateFoodEntryResultDTO,
)
from app.application.meal.ports.food_entry_repository_port import (
    FoodEntryRepositoryPort,
)
from app.application.meal.use_cases._helpers import food_entry_to_dto
from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.meal.errors import FoodEntryNotFoundError, InvalidMealTypeError
from app.domain.meal.value_objects import FoodEntryId, MealType


class UpdateFoodEntryUseCase:
    """
    既存の FoodEntry を更新する UseCase。

    - 現時点では「フル更新」前提。
    """

    def __init__(self, repo: FoodEntryRepositoryPort) -> None:
        self._repo = repo

    def execute(self, user_id: UserId, dto: UpdateFoodEntryInputDTO) -> UpdateFoodEntryResultDTO:
        entry_id = FoodEntryId(UUID(dto.entry_id))

        existing = self._repo.get_by_id(user_id, entry_id)
        if existing is None:
            raise FoodEntryNotFoundError(
                f"FoodEntry not found for id={dto.entry_id} user_id={user_id.value}"
            )

        # 変更前の日付を保持
        old_date = existing.date

        try:
            meal_type = MealType(dto.meal_type)
        except ValueError:
            raise InvalidMealTypeError(f"Invalid meal_type: {dto.meal_type}")

        # created_at / deleted_at は既存を維持、updated_at は None にして Repo/DB に任せる
        updated_entry = FoodEntry(
            id=existing.id,
            user_id=existing.user_id,
            date=dto.date,
            meal_type=meal_type,
            meal_index=dto.meal_index,
            name=dto.name,
            amount_value=dto.amount_value,
            amount_unit=dto.amount_unit,
            serving_count=dto.serving_count,
            note=dto.note,
            created_at=existing.created_at,
            updated_at=None,
            deleted_at=existing.deleted_at,
        )

        self._repo.update(updated_entry)

        updated_dto = food_entry_to_dto(updated_entry)

        # 更新後 DTO + 変更前の日付をまとめて返す
        return UpdateFoodEntryResultDTO(
            entry=updated_dto,
            old_date=old_date,
        )
