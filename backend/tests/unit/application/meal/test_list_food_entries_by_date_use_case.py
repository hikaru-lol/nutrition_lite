from __future__ import annotations

from datetime import date, datetime
from typing import Sequence
from uuid import uuid4

import pytest

from app.application.meal.dto.food_entry_dto import FoodEntryDTO
from app.application.meal.ports.food_entry_repository_port import FoodEntryRepositoryPort
from app.application.meal.use_cases.list_food_entries_by_date import (
    ListFoodEntriesByDateUseCase,
)
from app.application.meal.use_cases._helpers import food_entry_to_dto
from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.meal.value_objects import FoodEntryId, MealType
from tests.fakes.meal_uow import FakeMealUnitOfWork

pytestmark = pytest.mark.unit


class FakeFoodEntryRepository(FoodEntryRepositoryPort):
    def __init__(self) -> None:
        self.entries: list[FoodEntry] = []

    def add(self, entry: FoodEntry) -> None:  # pragma: no cover
        self.entries.append(entry)

    def update(self, entry: FoodEntry) -> None:  # pragma: no cover
        ...

    def delete(self, entry: FoodEntry) -> None:  # pragma: no cover
        ...

    def get_by_id(self, user_id: UserId, entry_id: FoodEntryId) -> FoodEntry | None:  # pragma: no cover
        return None

    def list_by_user_and_date(self, user_id: UserId, target_date: date) -> Sequence[FoodEntry]:
        return [
            e for e in self.entries
            if e.user_id == user_id and e.date == target_date and e.deleted_at is None
        ]

    def list_by_user_date_type_index(
        self,
        user_id: UserId,
        target_date: date,
        meal_type: MealType,
        meal_index: int | None,
    ) -> Sequence[FoodEntry]:  # pragma: no cover
        return []


def _make_user_id() -> UserId:
    return UserId(str(uuid4()))


def _make_entry(
    user_id: UserId,
    d: date,
    meal_type: MealType,
    meal_index: int | None,
    name: str,
) -> FoodEntry:
    eid = FoodEntryId(uuid4())
    now = datetime.utcnow()
    return FoodEntry(
        id=eid,
        user_id=user_id,
        date=d,
        meal_type=meal_type,
        meal_index=meal_index,
        name=name,
        amount_value=100.0,
        amount_unit="g",
        serving_count=None,
        note=None,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )


def test_list_meal_items_by_date_returns_only_that_day_and_user() -> None:
    repo = FakeFoodEntryRepository()
    use_case = ListFoodEntriesByDateUseCase(FakeMealUnitOfWork(repo))
    user1 = _make_user_id()
    user2 = _make_user_id()

    target_date = date(2025, 11, 24)
    other_date = date(2025, 11, 23)

    # 対象ユーザー + 対象日
    repo.entries.append(_make_entry(
        user1, target_date, MealType.MAIN, 1, "オートミール"))
    repo.entries.append(_make_entry(user1, target_date,
                        MealType.SNACK, None, "プロテインバー"))

    # 別日 / 別ユーザー
    repo.entries.append(_make_entry(user1, other_date, MealType.MAIN, 1, "別日"))
    repo.entries.append(_make_entry(
        user2, target_date, MealType.MAIN, 1, "別ユーザー"))

    result_dtos = use_case.execute(user1, target_date)

    assert len(result_dtos) == 2
    names = sorted(dto.name for dto in result_dtos)
    assert names == ["オートミール", "プロテインバー"]
