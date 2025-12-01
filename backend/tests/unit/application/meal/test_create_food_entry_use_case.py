from __future__ import annotations

from datetime import date
from typing import Sequence
from uuid import uuid4

import pytest

from app.application.meal.dto.food_entry_dto import CreateFoodEntryInputDTO
from app.application.meal.ports.food_entry_repository_port import FoodEntryRepositoryPort
from app.application.meal.use_cases.create_food_entry import CreateFoodEntryUseCase
from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.meal.errors import (
    InvalidMealTypeError,
    InvalidFoodAmountError,
)
from app.domain.meal.value_objects import FoodEntryId, MealType

pytestmark = pytest.mark.unit


class FakeFoodEntryRepository(FoodEntryRepositoryPort):
    """メモリ上に FoodEntry を保持するシンプルな Fake 実装。"""

    def __init__(self) -> None:
        self.entries: dict[str, FoodEntry] = {}

    # --- CRUD ---------------------------------------------------------

    def add(self, entry: FoodEntry) -> None:
        self.entries[str(entry.id.value)] = entry

    def update(self, entry: FoodEntry) -> None:  # pragma: no cover
        self.entries[str(entry.id.value)] = entry

    def delete(self, entry: FoodEntry) -> None:  # pragma: no cover
        self.entries.pop(str(entry.id.value), None)

    def get_by_id(self, user_id: UserId, entry_id: FoodEntryId) -> FoodEntry | None:  # pragma: no cover
        return self.entries.get(str(entry_id.value))

    # --- 検索 ---------------------------------------------------------

    def list_by_user_and_date(self, user_id: UserId, target_date: date) -> Sequence[FoodEntry]:  # pragma: no cover
        return [
            e for e in self.entries.values()
            if e.user_id == user_id and e.date == target_date and e.deleted_at is None
        ]

    def list_by_user_date_type_index(
        self,
        user_id: UserId,
        target_date: date,
        meal_type: MealType,
        meal_index: int | None,
    ) -> Sequence[FoodEntry]:  # pragma: no cover
        return [
            e for e in self.entries.values()
            if e.user_id == user_id
            and e.date == target_date
            and e.meal_type == meal_type
            and e.meal_index == meal_index
            and e.deleted_at is None
        ]


def _make_user_id() -> UserId:
    return UserId(str(uuid4()))


def test_create_main_meal_with_amount_value_and_unit() -> None:
    repo = FakeFoodEntryRepository()
    use_case = CreateFoodEntryUseCase(repo)
    user_id = _make_user_id()

    dto = CreateFoodEntryInputDTO(
        date=date(2025, 11, 24),
        meal_type="main",
        meal_index=1,
        name="鶏むね肉のソテー",
        amount_value=150.0,
        amount_unit="g",
        serving_count=None,
        note="オリーブオイルで調理",
    )

    result = use_case.execute(user_id, dto)

    assert result.id is not None
    assert result.date == dto.date
    assert result.meal_type == "main"
    assert result.meal_index == 1
    assert result.name == dto.name
    assert result.amount_value == 150.0
    assert result.amount_unit == "g"
    assert result.serving_count is None
    assert result.note == dto.note

    # Repo に保存されていることも確認
    assert len(repo.entries) == 1
    saved = next(iter(repo.entries.values()))
    assert saved.user_id == user_id
    assert saved.meal_type == MealType.MAIN


def test_create_snack_with_serving_count_only() -> None:
    repo = FakeFoodEntryRepository()
    use_case = CreateFoodEntryUseCase(repo)
    user_id = _make_user_id()

    dto = CreateFoodEntryInputDTO(
        date=date(2025, 11, 24),
        meal_type="snack",
        meal_index=None,
        name="プロテインバー",
        amount_value=None,
        amount_unit=None,
        serving_count=1.0,
        note=None,
    )

    result = use_case.execute(user_id, dto)

    assert result.meal_type == "snack"
    assert result.meal_index is None
    assert result.serving_count == 1.0
    assert len(repo.entries) == 1


def test_create_raises_invalid_meal_type() -> None:
    repo = FakeFoodEntryRepository()
    use_case = CreateFoodEntryUseCase(repo)
    user_id = _make_user_id()

    dto = CreateFoodEntryInputDTO(
        date=date(2025, 11, 24),
        meal_type="invalid",  # 👈 不正
        meal_index=1,
        name="何か",
        amount_value=100.0,
        amount_unit="g",
        serving_count=None,
        note=None,
    )

    with pytest.raises(InvalidMealTypeError):
        use_case.execute(user_id, dto)


def test_create_raises_invalid_food_amount_when_no_amount_specified() -> None:
    repo = FakeFoodEntryRepository()
    use_case = CreateFoodEntryUseCase(repo)
    user_id = _make_user_id()

    dto = CreateFoodEntryInputDTO(
        date=date(2025, 11, 24),
        meal_type="main",
        meal_index=1,
        name="何か",
        amount_value=None,
        amount_unit=None,
        serving_count=None,  # どちらも指定なし → NG
        note=None,
    )

    with pytest.raises(InvalidFoodAmountError):
        use_case.execute(user_id, dto)
