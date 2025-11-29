from __future__ import annotations

from datetime import date, datetime
from typing import Sequence
from uuid import uuid4

import pytest

from app.application.meal.ports.food_entry_repository_port import FoodEntryRepositoryPort
from app.application.meal.use_cases.delete_food_entry import DeleteFoodEntryUseCase
from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.meal.errors import FoodEntryNotFoundError
from app.domain.meal.value_objects import FoodEntryId, MealType
from tests.fakes.meal_uow import FakeMealUnitOfWork

pytestmark = pytest.mark.unit


class FakeFoodEntryRepository(FoodEntryRepositoryPort):
    def __init__(self) -> None:
        self.entries: dict[str, FoodEntry] = {}

    def add(self, entry: FoodEntry) -> None:
        self.entries[str(entry.id.value)] = entry

    def update(self, entry: FoodEntry) -> None:  # pragma: no cover
        self.entries[str(entry.id.value)] = entry

    def delete(self, entry: FoodEntry) -> None:
        # ソフトデリートの代わりにメモリ上から削除
        self.entries.pop(str(entry.id.value), None)

    def get_by_id(self, user_id: UserId, entry_id: FoodEntryId) -> FoodEntry | None:
        entry = self.entries.get(str(entry_id.value))
        if entry is None:
            return None
        if entry.user_id != user_id:
            return None
        return entry

    def list_by_user_and_date(self, user_id: UserId, target_date: date) -> Sequence[FoodEntry]:  # pragma: no cover
        return []

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


def _make_entry(user_id: UserId) -> FoodEntry:
    eid = FoodEntryId(uuid4())
    now = datetime.utcnow()
    return FoodEntry(
        id=eid,
        user_id=user_id,
        date=date(2025, 11, 24),
        meal_type=MealType.MAIN,
        meal_index=1,
        name="オートミール",
        amount_value=60.0,
        amount_unit="g",
        serving_count=None,
        note=None,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )


def test_delete_existing_entry_success() -> None:
    repo = FakeFoodEntryRepository()
    use_case = DeleteFoodEntryUseCase(FakeMealUnitOfWork(repo))
    user_id = _make_user_id()
    entry = _make_entry(user_id)
    repo.add(entry)

    use_case.execute(user_id, str(entry.id.value))

    assert str(entry.id.value) not in repo.entries


def test_delete_not_found_raises_error() -> None:
    repo = FakeFoodEntryRepository()
    use_case = DeleteFoodEntryUseCase(FakeMealUnitOfWork(repo))
    user_id = _make_user_id()

    with pytest.raises(FoodEntryNotFoundError):
        use_case.execute(user_id, str(uuid4()))
