from __future__ import annotations

import json
from datetime import date, datetime
from uuid import uuid4

import pytest

from app.application.nutrition.dto.daily_report_llm_dto import (
    DailyReportLLMInput,
)
from app.application.nutrition.errors import DailyReportGenerationFailedError
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_nutrition import DailyNutritionSummary
from app.domain.nutrition.meal_nutrition import MealNutritionSummary
from app.domain.profile.entities import Profile
from app.domain.profile.value_objects import HeightCm, Sex, WeightKg
from app.domain.target.entities import DailyTargetSnapshot, TargetNutrient
from app.domain.target.value_objects import (
    DEFAULT_NUTRIENT_UNITS,
    NutrientAmount,
    NutrientCode,
    NutrientSource,
    TargetId,
)
from app.domain.meal.value_objects import MealType
from app.infra.llm.daily_report_generator_openai import (
    OpenAIDailyNutritionReportGenerator,
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


def _build_target_nutrients() -> tuple[TargetNutrient, ...]:
    nutrients: list[TargetNutrient] = []
    for idx, code in enumerate(NutrientCode, start=1):
        nutrients.append(
            TargetNutrient(
                code=code,
                amount=NutrientAmount(
                    value=float(idx),
                    unit=DEFAULT_NUTRIENT_UNITS[code],
                ),
                source=NutrientSource("llm"),
            )
        )
    return tuple(nutrients)


def _make_input() -> DailyReportLLMInput:
    user_id = UserId(str(uuid4()))
    profile = Profile(
        user_id=user_id,
        sex=Sex.MALE,
        birthdate=date(1990, 1, 1),
        height_cm=HeightCm(175.0),
        weight_kg=WeightKg(70.0),
        image_id=None,
        meals_per_day=3,
    )
    target_snapshot = DailyTargetSnapshot(
        user_id=user_id,
        date=date(2024, 1, 1),
        target_id=TargetId("target-1"),
        nutrients=_build_target_nutrients(),
        created_at=datetime.utcnow(),
    )
    daily_summary = DailyNutritionSummary.from_nutrient_amounts(
        user_id=user_id,
        date=date(2024, 1, 1),
        nutrients=[
            (
                NutrientCode.PROTEIN,
                NutrientAmount(value=80.0, unit="g"),
            )
        ],
        source=NutrientSource("llm"),
    )
    meal_summary = MealNutritionSummary.from_nutrient_amounts(
        user_id=user_id,
        date=date(2024, 1, 1),
        meal_type=MealType.MAIN,
        meal_index=1,
        nutrients=[
            (
                NutrientCode.PROTEIN,
                NutrientAmount(value=30.0, unit="g"),
            )
        ],
        source=NutrientSource("llm"),
    )

    return DailyReportLLMInput(
        user_id=user_id,
        date=date(2024, 1, 1),
        profile=profile,
        target_snapshot=target_snapshot,
        daily_summary=daily_summary,
        meal_summaries=[meal_summary],
    )


def test_openai_daily_report_generator_success():
    response_obj = {
        "summary": "Great job today.",
        "good_points": ["Ate enough protein."],
        "improvement_points": ["Add more vegetables."],
        "tomorrow_focus": ["Plan a balanced breakfast."],
    }
    fake_client = FakeOpenAIClient(content=json.dumps(response_obj))
    generator = OpenAIDailyNutritionReportGenerator(client=fake_client)

    result = generator.generate(_make_input())

    assert result.summary == response_obj["summary"]
    assert result.good_points == response_obj["good_points"]
    assert result.improvement_points == response_obj["improvement_points"]
    assert result.tomorrow_focus == response_obj["tomorrow_focus"]


@pytest.mark.parametrize(
    "bad_data",
    [
        {
            "summary": 123,
            "good_points": ["ok"],
            "improvement_points": ["ok"],
            "tomorrow_focus": ["ok"],
        },
        {
            "summary": "ok",
            "good_points": [],
            "improvement_points": ["ok"],
            "tomorrow_focus": ["ok"],
        },
        {
            "summary": "ok",
            "good_points": ["ok"],
            "improvement_points": ["ok", 1],
            "tomorrow_focus": ["ok"],
        },
        {
            "summary": "ok",
            "good_points": ["ok"],
            "improvement_points": ["ok"],
        },
    ],
)
def test_openai_daily_report_generator_invalid_fields_raise(bad_data):
    fake_client = FakeOpenAIClient(content=json.dumps(bad_data))
    generator = OpenAIDailyNutritionReportGenerator(client=fake_client)

    with pytest.raises(DailyReportGenerationFailedError):
        generator.generate(_make_input())
