from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from openai import OpenAI, OpenAIError

from app.application.nutrition.dto.meal_recommendation_llm_dto import (
    MealRecommendationLLMInput,
    MealRecommendationLLMOutput,
)
from app.application.nutrition.ports.recommendation_generator_port import (
    MealRecommendationGeneratorPort,
)

from app.domain.nutrition.errors import NutritionDomainError  # 既存のベース
# なければ専用エラーを追加してもOK
# from app.domain.nutrition.errors import MealRecommendationGenerationFailedError など

logger = logging.getLogger(__name__)


class MealRecommendationGenerationFailedError(NutritionDomainError):
    """提案生成（LLM）が失敗した場合のエラー。"""


_SYSTEM_PROMPT = """\
You are a registered dietitian and nutrition coach.

Your task:
Given a user's recent daily nutrition reports and profile,
propose practical suggestions on how they can eat in the next few days. 

You MUST return ONLY a single JSON object with the following structure:

{
  "body": "<main recommendation text as 1-3 short paragraphs>",
  "tips": ["<tip 1>", "<tip 2>", "..."]
}

Requirements:

- "body" must be a friendly, concise summary (1-3 short paragraphs).
- "tips" must be a JSON array of short, actionable suggestions (strings).
- Always include at least 2 tips.
- Use safe, general wellness advice. Do NOT provide medical diagnoses.
- Do NOT mention specific diseases or medications.
- Do NOT include any extra keys outside this JSON object.
"""


@dataclass(slots=True)
class OpenAIMealRecommendationGeneratorConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.4


class OpenAIMealRecommendationGenerator(MealRecommendationGeneratorPort):
    """
    OpenAI Chat Completions API を使って MealRecommendation を生成する実装。

    - OPENAI_API_KEY は環境変数から読み込む前提。
    - JSON モードで body / tips を返させて MealRecommendationLLMOutput にマッピングする。
    """

    def __init__(
        self,
        client: OpenAI | None = None,
        config: OpenAIMealRecommendationGeneratorConfig | None = None,

    ) -> None:
        self._client = client or OpenAI()
        self._config = config or OpenAIMealRecommendationGeneratorConfig()
    # ------------------------------------------------------------------
    # Port 実装
    # ------------------------------------------------------------------

    def generate(
        self,
        input: MealRecommendationLLMInput,
    ) -> MealRecommendationLLMOutput:

        user_prompt = self._build_user_prompt(input)

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
            logger.exception(
                "OpenAI API error while generating meal recommendation: user=%s base_date=%s",
                input.user_id.value,
                input.base_date,
            )
            raise MealRecommendationGenerationFailedError(
                "Failed to generate meal recommendation via OpenAI"
            ) from e

        content = completion.choices[0].message.content
        if content is None:
            raise MealRecommendationGenerationFailedError(
                "OpenAI returned empty content for meal recommendation"
            )

        try:
            data: dict[str, Any] = json.loads(content)
        except json.JSONDecodeError as e:
            logger.exception(
                "Failed to parse JSON from meal recommendation response: %s",
                content,
            )
            raise MealRecommendationGenerationFailedError(
                "Failed to parse JSON from meal recommendation response"
            ) from e

        try:
            return self._to_output_dto(data)
        except Exception as e:
            logger.exception(
                "Failed to map JSON to MealRecommendationLLMOutput: %s",
                data,
            )
            raise MealRecommendationGenerationFailedError(
                "Failed to map JSON to MealRecommendationLLMOutput"
            ) from e

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    def _build_user_prompt(self, input: MealRecommendationLLMInput) -> str:
        """
        プロフィール + 直近レポートを LLM に渡すテキストにまとめる。
        """

        p = input.profile
        reports = input.recent_reports

        lines: list[str] = []

        lines.append(f"User ID: {input.user_id.value}")
        lines.append(f"Base date: {input.base_date.isoformat()}")
        lines.append("")
        lines.append("User profile:")
        lines.append(f"- Sex: {p.sex}")
        lines.append(f"- Birthdate: {p.birthdate}")
        lines.append(f"- Height: {p.height_cm} cm")
        lines.append(f"- Weight: {p.weight_kg} kg")
        lines.append(f"- Meals per day: {p.meals_per_day}")
        lines.append("")

        lines.append(
            f"Recent daily nutrition reports (latest {len(reports)} days):")
        for r in reports:
            lines.append(f"- Date: {r.date}")
            lines.append(f"  Summary: {r.summary}")
            if r.good_points:
                lines.append(f"  Good points: {', '.join(r.good_points)}")
            if r.improvement_points:
                lines.append(
                    f"  Improvement points: {', '.join(r.improvement_points)}")
            if r.tomorrow_focus:
                lines.append(
                    f"  Tomorrow focus: {', '.join(r.tomorrow_focus)}")
            lines.append("")

        lines.append(
            "Based on these trends, propose what the user should focus on "
            "in the next few days, following the JSON format specified by the system."
        )

        return "\n".join(lines)

    def _to_output_dto(self, data: dict[str, Any]) -> MealRecommendationLLMOutput:
        """
        JSON データ -> MealRecommendationLLMOutput への変換とバリデーション。
        """

        def _ensure_str(value: Any, field: str) -> str:
            if not isinstance(value, str):
                raise ValueError(f"{field} must be string")
            return value

        def _ensure_str_list(value: Any, field: str) -> list[str]:
            if not isinstance(value, list) or not value:
                raise ValueError(
                    f"{field} must be a non-empty list of strings")
            result: list[str] = []
            for i, v in enumerate(value):
                if not isinstance(v, str):
                    raise ValueError(f"{field}[{i}] must be string")
                result.append(v)
            return result

        body = _ensure_str(data.get("body"), "body")
        tips = _ensure_str_list(data.get("tips"), "tips")

        return MealRecommendationLLMOutput(
            body=body,
            tips=tips,
        )
