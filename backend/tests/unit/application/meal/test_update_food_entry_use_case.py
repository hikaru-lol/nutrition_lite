from __future__ import annotations

from datetime import date, datetime
from typing import Sequence
from uuid import uuid4, UUID

import pytest

from app.application.meal.dto.food_entry_dto import UpdateFoodEntryInputDTO
from app.application.meal.ports.food_entry_repository_port import FoodEntryRepositoryPort
from app.application.meal.use_cases.update_food_entry import UpdateFoodEntryUseCase
from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.meal.errors import (
    InvalidMealTypeError,
    FoodEntryNotFoundError,
)
from app.domain.meal.value_objects import FoodEntryId, MealType
from tests.fakes.meal_uow import FakeMealUnitOfWork

pytestmark = pytest.mark.unit


class FakeFoodEntryRepository(FoodEntryRepositoryPort):
    def __init__(self) -> None:
        self.entries: dict[str, FoodEntry] = {}

    def add(self, entry: FoodEntry) -> None:
        self.entries[str(entry.id.value)] = entry

    def update(self, entry: FoodEntry) -> None:
        self.entries[str(entry.id.value)] = entry

    def delete(self, entry: FoodEntry) -> None:  # pragma: no cover
        self.entries.pop(str(entry.id.value), None)

    def get_by_id(self, user_id: UserId, entry_id: FoodEntryId) -> FoodEntry | None:
        entry = self.entries.get(str(entry_id.value))
        if entry is None:
            return None
        if entry.user_id != user_id:
            return None
        if entry.deleted_at is not None:
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


def _make_existing_entry(user_id: UserId) -> FoodEntry:
    entry_id = FoodEntryId(uuid4())
    now = datetime.utcnow()
    return FoodEntry(
        id=entry_id,
        user_id=user_id,
        date=date(2025, 11, 24),
        meal_type=MealType.MAIN,
        meal_index=1,
        name="オートミール",
        amount_value=60.0,
        amount_unit="g",
        serving_count=None,
        note="before",
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )


def test_update_existing_entry_success() -> None:
    repo = FakeFoodEntryRepository()
    use_case = UpdateFoodEntryUseCase(FakeMealUnitOfWork(repo))
    user_id = _make_user_id()

    existing = _make_existing_entry(user_id)
    repo.add(existing)

    dto = UpdateFoodEntryInputDTO(
        entry_id=str(existing.id.value),
        date=date(2025, 11, 25),  # 日付も更新
        meal_type="main",
        meal_index=2,
        name="鶏むね肉のソテー",
        amount_value=150.0,
        amount_unit="g",
        serving_count=None,
        note="after",
    )

    result = use_case.execute(user_id, dto)

    assert result.entry.id == str(existing.id.value)
    assert result.entry.date == dto.date
    assert result.entry.meal_type == "main"
    assert result.entry.meal_index == 2
    assert result.entry.name == "鶏むね肉のソテー"
    assert result.entry.amount_value == 150.0
    assert result.entry.note == "after"
    assert result.old_date == date(2025, 11, 24)

    # Repo に反映されているか確認
    saved = repo.entries[str(existing.id.value)]
    assert saved.date == dto.date
    assert saved.meal_index == 2
    assert saved.name == dto.name


def test_update_not_found_raises_error() -> None:
    repo = FakeFoodEntryRepository()
    use_case = UpdateFoodEntryUseCase(FakeMealUnitOfWork(repo))
    user_id = _make_user_id()

    dto = UpdateFoodEntryInputDTO(
        entry_id=str(uuid4()),  # 存在しない ID
        date=date(2025, 11, 24),
        meal_type="main",
        meal_index=1,
        name="何か",
        amount_value=100.0,
        amount_unit="g",
        serving_count=None,
        note=None,
    )

    with pytest.raises(FoodEntryNotFoundError):
        use_case.execute(user_id, dto)


def test_update_invalid_meal_type_raises_error() -> None:
    repo = FakeFoodEntryRepository()
    use_case = UpdateFoodEntryUseCase(FakeMealUnitOfWork(repo))
    user_id = _make_user_id()

    existing = _make_existing_entry(user_id)
    repo.add(existing)

    dto = UpdateFoodEntryInputDTO(
        entry_id=str(existing.id.value),
        date=existing.date,
        meal_type="invalid",  # 👈 不正
        meal_index=existing.meal_index,
        name=existing.name,
        amount_value=existing.amount_value,
        amount_unit=existing.amount_unit,
        serving_count=existing.serving_count,
        note=existing.note,
    )

    with pytest.raises(InvalidMealTypeError):
        use_case.execute(user_id, dto)
