from __future__ import annotations

import json
from datetime import date
from uuid import uuid4

import pytest
from openai import OpenAIError  # 例外テスト用

from app.application.target.ports.target_generator_port import (
    TargetGenerationContext,
)
from app.domain.auth.value_objects import UserId
from app.domain.target.entities import TargetNutrient
from app.domain.target.value_objects import (
    GoalType,
    ActivityLevel,
    NutrientCode,
)
from app.application.target.errors import TargetGenerationFailedError
from app.infra.llm.target_generator_openai import (
    OpenAITargetGenerator,
    OpenAITargetGeneratorConfig,
)


# =====================================================================
# Fake OpenAI Client 実装群
# =====================================================================


class _FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeChoice:
    def __init__(self, content: str) -> None:
        self.message = _FakeMessage(content)


class _FakeCompletion:
    def __init__(self, content: str) -> None:
        self.choices = [_FakeChoice(content)]


class _FakeChatCompletions:
    def __init__(self, content: str) -> None:
        self._content = content

    def create(self, *args, **kwargs) -> _FakeCompletion:  # 引数は無視
        return _FakeCompletion(self._content)


class _FakeChat:
    def __init__(self, content: str) -> None:
        self.completions = _FakeChatCompletions(content)


class FakeOpenAIClient:
    """
    OpenAI クライアントのフェイク。

    - chat.completions.create(...) を呼ぶと、
      事前に渡された content を返す。
    """

    def __init__(self, content: str) -> None:
        self.chat = _FakeChat(content)


class ErrorOpenAIClient:
    """
    chat.completions.create(...) が OpenAIError を投げるフェイク。
    """

    def __init__(self, error: OpenAIError) -> None:
        self._error = error
        self.chat = self  # chat.completions の代わりに self で受ける

    class completions:
        pass  # ダミー（型だけ）

    def completions(self):
        return self

    def create(self, *args, **kwargs):
        raise self._error


# =====================================================================
# Helper: TargetGenerationContext を作る
# =====================================================================


def make_ctx() -> TargetGenerationContext:
    user_id = UserId(str(uuid4()))
    return TargetGenerationContext(
        user_id=user_id,
        sex="male",
        birthdate=date(1990, 1, 1),
        height_cm=175.0,
        weight_kg=70.0,
        goal_type=GoalType.WEIGHT_LOSS,
        activity_level=ActivityLevel.NORMAL,
    )


# =====================================================================
# 正常系
# =====================================================================


def test_openai_target_generator_success():
    # 17 栄養素ぶんの JSON を用意
    nutrients_json = {
        "carbohydrate": {"amount": 250.0, "unit": "g"},
        "fat": {"amount": 60.0, "unit": "g"},
        "protein": {"amount": 120.0, "unit": "g"},
        "vitamin_a": {"amount": 900.0, "unit": "µg"},
        "vitamin_b_complex": {"amount": 50.0, "unit": "mg"},
        "vitamin_c": {"amount": 100.0, "unit": "mg"},
        "vitamin_d": {"amount": 20.0, "unit": "µg"},
        "vitamin_e": {"amount": 10.0, "unit": "mg"},
        "vitamin_k": {"amount": 150.0, "unit": "µg"},
        "calcium": {"amount": 700.0, "unit": "mg"},
        "iron": {"amount": 10.0, "unit": "mg"},
        "magnesium": {"amount": 300.0, "unit": "mg"},
        "zinc": {"amount": 10.0, "unit": "mg"},
        "sodium": {"amount": 1500.0, "unit": "mg"},
        "potassium": {"amount": 2500.0, "unit": "mg"},
        "fiber": {"amount": 20.0, "unit": "g"},
        "water": {"amount": 2000.0, "unit": "ml"},
    }

    response_obj = {
        "nutrients": nutrients_json,
        "llm_rationale": "test rationale",
        "disclaimer": "test disclaimer",
    }

    content = json.dumps(response_obj)
    fake_client = FakeOpenAIClient(content=content)

    generator = OpenAITargetGenerator(
        client=fake_client,
        config=OpenAITargetGeneratorConfig(
            model="gpt-4o-mini", temperature=0.0),
    )

    ctx = make_ctx()
    result = generator.generate(ctx)

    # 17 栄養素ぶん返っていること
    assert len(result.nutrients) == len(list(NutrientCode))

    # 各栄養素が JSON の値どおりにマッピングされていること
    mapping = {n.code.value: n for n in result.nutrients}
    for code in NutrientCode:
        key = code.value
        assert key in mapping
        tn: TargetNutrient = mapping[key]
        expected = nutrients_json[key]
        assert tn.amount.value == expected["amount"]
        assert tn.amount.unit == expected["unit"]
        assert tn.source.value == "llm"

    assert result.llm_rationale == "test rationale"
    assert result.disclaimer == "test disclaimer"


# =====================================================================
# 異常系: JSON パースエラー
# =====================================================================


def test_openai_target_generator_invalid_json_raises():
    fake_client = FakeOpenAIClient(content="this is not json")

    generator = OpenAITargetGenerator(
        client=fake_client,
        config=OpenAITargetGeneratorConfig(
            model="gpt-4o-mini", temperature=0.0),
    )

    ctx = make_ctx()
    with pytest.raises(TargetGenerationFailedError):
        generator.generate(ctx)


# =====================================================================
# 異常系: nutrients の key が不足している
# =====================================================================


def test_openai_target_generator_missing_nutrient_raises():
    # 故意に fiber を欠けさせる
    nutrients_json = {
        "carbohydrate": {"amount": 250.0, "unit": "g"},
        "fat": {"amount": 60.0, "unit": "g"},
        "protein": {"amount": 120.0, "unit": "g"},
        "vitamin_a": {"amount": 900.0, "unit": "µg"},
        "vitamin_b_complex": {"amount": 50.0, "unit": "mg"},
        "vitamin_c": {"amount": 100.0, "unit": "mg"},
        "vitamin_d": {"amount": 20.0, "unit": "µg"},
        "vitamin_e": {"amount": 10.0, "unit": "mg"},
        "vitamin_k": {"amount": 150.0, "unit": "µg"},
        "calcium": {"amount": 700.0, "unit": "mg"},
        "iron": {"amount": 10.0, "unit": "mg"},
        "magnesium": {"amount": 300.0, "unit": "mg"},
        "zinc": {"amount": 10.0, "unit": "mg"},
        "sodium": {"amount": 1500.0, "unit": "mg"},
        "potassium": {"amount": 2500.0, "unit": "mg"},
        # "fiber": {"amount": 20.0, "unit": "g"},  # わざと抜く
        "water": {"amount": 2000.0, "unit": "ml"},
    }

    response_obj = {
        "nutrients": nutrients_json,
        "llm_rationale": "test rationale",
        "disclaimer": "test disclaimer",
    }

    fake_client = FakeOpenAIClient(content=json.dumps(response_obj))

    generator = OpenAITargetGenerator(
        client=fake_client,
        config=OpenAITargetGeneratorConfig(
            model="gpt-4o-mini", temperature=0.0),
    )

    ctx = make_ctx()
    with pytest.raises(TargetGenerationFailedError):
        generator.generate(ctx)


# =====================================================================
# 異常系: OpenAI API 側のエラー
# =====================================================================


class _DummyOpenAIError(OpenAIError):
    pass


class RaisingOpenAIClient:
    """
    chat.completions.create を呼ぶと OpenAIError を投げるクライアント。
    """

    def __init__(self) -> None:
        self.chat = self

    class completions:  # ダミー
        pass

    def completions(self):  # 型の都合で
        return self

    def create(self, *args, **kwargs):
        raise _DummyOpenAIError("dummy error from OpenAI")


def test_openai_target_generator_openai_error_raises():
    fake_client = RaisingOpenAIClient()

    generator = OpenAITargetGenerator(
        client=fake_client,
        config=OpenAITargetGeneratorConfig(
            model="gpt-4o-mini", temperature=0.0),
    )

    ctx = make_ctx()
    with pytest.raises(TargetGenerationFailedError):
        generator.generate(ctx)
