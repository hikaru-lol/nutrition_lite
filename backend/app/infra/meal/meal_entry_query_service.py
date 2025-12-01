from app.application.nutrition.ports.meal_entry_query_port import (
    MealEntryQueryPort,
)
from app.application.meal.ports.uow_port import MealUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.meal.value_objects import MealType
from datetime import date as DateType
from typing import Sequence
from app.domain.meal.entities import FoodEntry


class MealEntryQueryService(MealEntryQueryPort):
    def __init__(self, meal_uow: MealUnitOfWorkPort) -> None:
        self._meal_uow = meal_uow

    def list_entries_for_meal(
        self,
        user_id: UserId,
        date_: DateType,
        meal_type: MealType,
        meal_index: int | None,
    ) -> Sequence[FoodEntry]:
        with self._meal_uow as uow:
            return list(
                uow.food_entry_repo.list_by_user_date_type_index(
                    user_id=user_id,
                    target_date=date_,
                    meal_type=meal_type,
                    meal_index=meal_index,
                )
            )
