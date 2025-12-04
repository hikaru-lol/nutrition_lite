from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import date
from typing import Any

from openai import OpenAI, OpenAIError  # pip install openai>=1.0.0

from app.application.target.ports.target_generator_port import (
    TargetGeneratorPort,
    TargetGenerationContext,
    TargetGenerationResult,
)
from app.domain.target.entities import TargetNutrient
from app.domain.target.value_objects import (
    NutrientCode,
    NutrientAmount,
    NutrientSource,
)
from app.application.target.errors import TargetGenerationFailedError


logger = logging.getLogger(__name__)


_SYSTEM_PROMPT = """\
You are a registered dietitian and nutrition expert.

Your task:
Given a user's profile (sex, age, height, weight), activity level, and goal,
you must propose a daily target amount for the following 10 nutrients:

- carbohydrate (g)  # 炭水化物
- fat (g)           # 脂質
- protein (g)       # たんぱく質
- water (ml)        # 水分
- fiber (g)         # 食物繊維
- sodium (mg)       # ナトリウム
- iron (mg)         # 鉄
- calcium (mg)      # カルシウム
- vitamin_d (µg)    # ビタミンD
- potassium (mg)    # カリウム

Output requirements (IMPORTANT):

- Return ONLY a single JSON object.
- The top-level structure MUST be:

{
  "nutrients": {
    "carbohydrate": {"amount": <number>, "unit": "g"},
    "fat":          {"amount": <number>, "unit": "g"},
    "protein":      {"amount": <number>, "unit": "g"},
    "water":        {"amount": <number>, "unit": "ml"},
    "fiber":        {"amount": <number>, "unit": "g"},
    "sodium":       {"amount": <number>, "unit": "mg"},
    "iron":         {"amount": <number>, "unit": "mg"},
    "calcium":      {"amount": <number>, "unit": "mg"},
    "vitamin_d":    {"amount": <number>, "unit": "µg"},
    "potassium":    {"amount": <number>, "unit": "mg"}
  },
  "llm_rationale": "<string explaining the reasoning>",
  "disclaimer": "<string reminding it is not medical advice>"
}

- Use realistic, safe ranges for a healthy adult.
- Adjust amounts based on activity level and goal (weight_loss / maintain / weight_gain / health_improve).
- If some profile info is missing, make reasonable generic assumptions.
- Do NOT include any extra keys or text outside this JSON object.
"""


@dataclass(slots=True)
class OpenAITargetGeneratorConfig:
    model: str = "gpt-4o-mini"  # 好きなモデルに変えてOK
    temperature: float = 0.2
    # 必要に応じて max_tokens なども追加可能


class OpenAITargetGenerator(TargetGeneratorPort):
    """
    OpenAI Chat Completions API を使って 10 栄養素のターゲットを生成する実装。

    - env の OPENAI_API_KEY を利用して認証する想定。
    """

    def __init__(
        self,
        client: OpenAI | None = None,
        config: OpenAITargetGeneratorConfig | None = None,
    ) -> None:
        self._client = client or OpenAI()  # OPENAI_API_KEY を自動で読む
        self._config = config or OpenAITargetGeneratorConfig()

    def generate(self, ctx: TargetGenerationContext) -> TargetGenerationResult:
        """
        Profile + goal 情報をもとに LLM に JSON 形式で 10 栄養素のターゲット生成を依頼。
        """
        user_prompt = self._build_user_prompt(ctx)

        try:
            completion = self._client.chat.completions.create(
                model=self._config.model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self._config.temperature,
                response_format={"type": "json_object"},
            )
        except OpenAIError as e:
            logger.exception("OpenAI API error while generating target: %s", e)
            raise TargetGenerationFailedError(
                "Failed to generate target via OpenAI"
            ) from e

        content = completion.choices[0].message.content
        if content is None:
            raise TargetGenerationFailedError("OpenAI returned empty content")

        try:
            data: dict[str, Any] = json.loads(content)
        except json.JSONDecodeError as e:
            logger.exception(
                "Failed to parse JSON from OpenAI response: %s", content
            )
            raise TargetGenerationFailedError(
                "Failed to parse JSON from OpenAI response"
            ) from e

        try:
            nutrients = self._parse_nutrients(data.get("nutrients", {}))
        except Exception as e:
            logger.exception(
                "Failed to map nutrients from OpenAI response: %s", data
            )
            raise TargetGenerationFailedError(
                "Failed to map nutrients from OpenAI response"
            ) from e

        llm_rationale = data.get("llm_rationale")
        disclaimer = data.get("disclaimer")

        return TargetGenerationResult(
            nutrients=nutrients,
            llm_rationale=llm_rationale,
            disclaimer=disclaimer,
        )

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    def _build_user_prompt(self, ctx: TargetGenerationContext) -> str:
        """
        ユーザーのプロフィール情報を LLM に渡すためのテキストにまとめる。
        """
        # 年齢をざっくり計算（birthdate があれば）
        age_str = "unknown"
        if ctx.birthdate is not None:
            today = date.today()
            age = today.year - ctx.birthdate.year - (
                (today.month, today.day)
                < (ctx.birthdate.month, ctx.birthdate.day)
            )
            age_str = f"{age} years"

        sex_str = ctx.sex or "unknown"
        height_str = (
            f"{ctx.height_cm:.1f} cm" if ctx.height_cm is not None else "unknown"
        )
        weight_str = (
            f"{ctx.weight_kg:.1f} kg" if ctx.weight_kg is not None else "unknown"
        )

        prompt = f"""
User profile:
- Sex: {sex_str}
- Age: {age_str}
- Height: {height_str}
- Weight: {weight_str}

Goal information:
- Goal type: {ctx.goal_type.value}
- Activity level: {ctx.activity_level.value}

Please propose daily target amounts for the 10 nutrients described in the system prompt.
""".strip()

        return prompt

    def _parse_nutrients(self, raw_nutrients: dict[str, Any]) -> list[TargetNutrient]:
        """
        LLM から返ってきた JSON の "nutrients" 部分を TargetNutrient のリストに変換する。

        - NutrientCode Enum に定義されている 10 栄養素分をすべて揃っている前提。
        """
        nutrients: list[TargetNutrient] = []

        for code in NutrientCode:
            key = code.value
            if key not in raw_nutrients:
                raise ValueError(f"Missing nutrient in response: {key}")

            entry = raw_nutrients[key]
            amount_val = float(entry["amount"])
            unit = str(entry["unit"])

            nutrients.append(
                TargetNutrient(
                    code=code,
                    amount=NutrientAmount(value=amount_val, unit=unit),
                    source=NutrientSource("llm"),
                )
            )

        return nutrients
