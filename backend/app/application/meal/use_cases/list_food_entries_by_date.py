from __future__ import annotations

from datetime import date
from typing import Sequence

from app.application.meal.dto.food_entry_dto import FoodEntryDTO
from app.application.meal.use_cases._helpers import food_entry_to_dto

from app.application.meal.ports.uow_port import MealUnitOfWorkPort

from app.domain.auth.value_objects import UserId


class ListFoodEntriesByDateUseCase:
    """
    指定した 1 日分の FoodEntry 一覧を返す UseCase。

    - main / snack を区別せず、その日の全ログを返す。
    - ソート順は Repository 側の実装に依存
      （現状: date, meal_type, meal_index, created_at で昇順の想定）。
    """

    def __init__(self, meal_uow: MealUnitOfWorkPort) -> None:
        self._meal_uow = meal_uow

    def execute(self, user_id: UserId, target_date: date) -> Sequence[FoodEntryDTO]:
        with self._meal_uow as uow:
            entries = uow.food_entry_repo.list_by_user_and_date(
                user_id, target_date)
        return [food_entry_to_dto(e) for e in entries]
