from typing import Protocol, Sequence
from datetime import date as DateType
from app.domain.auth.value_objects import UserId
from app.domain.meal.value_objects import MealType
from app.domain.meal.entities import FoodEntry  # ここは現状の Entity をそのまま使う


class MealEntryQueryPort(Protocol):
    def list_entries_for_meal(
        self,
        user_id: UserId,
        date_: DateType,
        meal_type: MealType,
        meal_index: int | None,
    ) -> Sequence[FoodEntry]:
        ...
