from __future__ import annotations

import json
from datetime import date
from uuid import uuid4

from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.meal.value_objects import FoodEntryId, MealType
from app.infra.llm.estimator_openai import (
    EXPECTED_CODES,
    EXPECTED_UNITS,
    OpenAINutritionEstimator,
)


class _FakeMessage:
    def __init__(self, content: str | None) -> None:
        self.content = content


class _FakeChoice:
    def __init__(self, content: str | None) -> None:
        self.message = _FakeMessage(content)


class _FakeCompletion:
    def __init__(self, content: str | None) -> None:
        self.choices = [_FakeChoice(content)]


class _FakeChatCompletions:
    def __init__(self, content: str | None) -> None:
        self._content = content

    def create(self, *args, **kwargs) -> _FakeCompletion:
        return _FakeCompletion(self._content)


class _FakeChat:
    def __init__(self, completions: _FakeChatCompletions) -> None:
        self.completions = completions


class FakeOpenAIClient:
    def __init__(self, content: str | None) -> None:
        self.chat = _FakeChat(_FakeChatCompletions(content))


def _make_entry(user_id: UserId) -> FoodEntry:
    return FoodEntry(
        id=FoodEntryId.new(),
        user_id=user_id,
        date=date(2024, 1, 1),
        meal_type=MealType.MAIN,
        meal_index=1,
        name="chicken salad",
        amount_value=150.0,
        amount_unit="g",
        serving_count=None,
        note=None,
    )


def _build_nutrients_data() -> dict[str, dict[str, object]]:
    nutrients: dict[str, dict[str, object]] = {}
    for idx, code in enumerate(EXPECTED_CODES, start=1):
        nutrients[code.value] = {
            "amount": float(idx),
            "unit": EXPECTED_UNITS[code],
        }
    return nutrients


def test_openai_nutrition_estimator_success():
    expected = _build_nutrients_data()
    response_obj = {"nutrients": expected}
    fake_client = FakeOpenAIClient(content=json.dumps(response_obj))

    estimator = OpenAINutritionEstimator(client=fake_client)
    user_id = UserId(str(uuid4()))

    result = estimator.estimate_for_entries(
        user_id=user_id,
        date=date(2024, 1, 1),
        entries=[_make_entry(user_id)],
    )

    assert len(result) == len(EXPECTED_CODES)
    mapping = {n.code: n for n in result}
    for code in EXPECTED_CODES:
        assert code in mapping
        intake = mapping[code]
        assert intake.amount.unit == EXPECTED_UNITS[code]
        assert intake.amount.value == expected[code.value]["amount"]
        assert intake.code == code


def test_openai_nutrition_estimator_empty_entries_returns_empty():
    fake_client = FakeOpenAIClient(content=json.dumps({"nutrients": {}}))
    estimator = OpenAINutritionEstimator(client=fake_client)
    user_id = UserId(str(uuid4()))

    result = estimator.estimate_for_entries(
        user_id=user_id,
        date=date(2024, 1, 1),
        entries=[],
    )

    assert result == []
