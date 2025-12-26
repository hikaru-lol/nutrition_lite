from __future__ import annotations

import json
from datetime import date
from uuid import uuid4

import pytest

from app.application.target.errors import TargetGenerationFailedError
from app.application.target.ports.target_generator_port import (
    TargetGenerationContext,
)
from app.domain.auth.value_objects import UserId
from app.domain.target.value_objects import (
    ActivityLevel,
    DEFAULT_NUTRIENT_UNITS,
    GoalType,
    NutrientCode,
)
from app.infra.llm.target_generator_openai import (
    OpenAITargetGenerator,
    OpenAITargetGeneratorConfig,
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
        self.last_kwargs: dict | None = None

    def create(self, *args, **kwargs) -> _FakeCompletion:
        self.last_kwargs = kwargs
        return _FakeCompletion(self._content)


class _FakeChat:
    def __init__(self, completions: _FakeChatCompletions) -> None:
        self.completions = completions


class FakeOpenAIClient:
    def __init__(self, content: str | None) -> None:
        completions = _FakeChatCompletions(content)
        self.chat = _FakeChat(completions)


def _make_ctx() -> TargetGenerationContext:
    return TargetGenerationContext(
        user_id=UserId(str(uuid4())),
        sex="male",
        birthdate=date(1990, 1, 1),
        height_cm=175.0,
        weight_kg=70.0,
        goal_type=GoalType.WEIGHT_LOSS,
        activity_level=ActivityLevel.NORMAL,
    )


def _build_nutrients_data() -> dict[str, dict[str, object]]:
    nutrients: dict[str, dict[str, object]] = {}
    for idx, code in enumerate(NutrientCode, start=1):
        nutrients[code.value] = {
            "amount": float(idx),
            "unit": DEFAULT_NUTRIENT_UNITS[code],
        }
    return nutrients


def test_openai_target_generator_sets_rationale_and_disclaimer():
    response_obj = {
        "nutrients": _build_nutrients_data(),
        "llm_rationale": "test rationale",
        "disclaimer": "test disclaimer",
    }
    fake_client = FakeOpenAIClient(content=json.dumps(response_obj))

    generator = OpenAITargetGenerator(
        client=fake_client,
        config=OpenAITargetGeneratorConfig(
            model="gpt-4o-mini",
            temperature=0.3,
        ),
    )

    result = generator.generate(_make_ctx())

    assert result.llm_rationale == "test rationale"
    assert result.disclaimer == "test disclaimer"

    call_kwargs = fake_client.chat.completions.last_kwargs
    assert call_kwargs is not None
    assert call_kwargs["model"] == "gpt-4o-mini"
    assert call_kwargs["temperature"] == 0.3
    assert call_kwargs["response_format"] == {"type": "json_object"}


def test_openai_target_generator_content_none_raises():
    fake_client = FakeOpenAIClient(content=None)
    generator = OpenAITargetGenerator(client=fake_client)

    with pytest.raises(TargetGenerationFailedError):
        generator.generate(_make_ctx())


@pytest.mark.parametrize(
    "mutate",
    [
        lambda nutrients: nutrients["protein"].pop("amount"),
        lambda nutrients: nutrients["protein"].__setitem__("amount", "nope"),
        lambda nutrients: nutrients["protein"].pop("unit"),
    ],
)
def test_openai_target_generator_invalid_nutrient_entry_raises(mutate):
    nutrients = _build_nutrients_data()
    mutate(nutrients)

    response_obj = {"nutrients": nutrients}
    fake_client = FakeOpenAIClient(content=json.dumps(response_obj))
    generator = OpenAITargetGenerator(client=fake_client)

    with pytest.raises(TargetGenerationFailedError):
        generator.generate(_make_ctx())
