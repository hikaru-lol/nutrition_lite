from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from openai import OpenAI, OpenAIError

from app.application.nutrition.dto.daily_report_llm_dto import (
    DailyReportLLMInput,
    DailyReportLLMOutput,
)
from app.application.nutrition.ports.daily_report_generator_port import (
    DailyNutritionReportGeneratorPort,
)
from app.application.nutrition.errors import DailyReportGenerationFailedError  # なければ作成
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_nutrition import DailyNutritionSummary
from app.domain.nutrition.meal_nutrition import MealNutritionSummary
from app.domain.profile.entities import Profile
from app.domain.target.entities import DailyTargetSnapshot

logger = logging.getLogger(__name__)


_SYSTEM_PROMPT = """\
You are a registered dietitian and nutrition coach.

Your task:
Given a user's profile, daily nutrition summary, meal-level summaries, and target snapshot,
you must write a friendly, concise daily nutrition report.

You MUST return ONLY a single JSON object with the following structure:

{
  "summary": "<overall summary as a short paragraph>",
  "good_points": ["<bullet 1>", "<bullet 2>", "..."],
  "improvement_points": ["<bullet 1>", "<bullet 2>", "..."],
  "tomorrow_focus": ["<bullet 1>", "<bullet 2>", "..."]
}

Requirements:

- "summary" must be a short paragraph (2-5 sentences).
- "good_points", "improvement_points", and "tomorrow_focus" must each be
  a JSON array of strings (bulleted advice).
- Use safe, general wellness advice. Do NOT provide medical diagnoses.
- Always include at least one item in each array.
- Do NOT include any extra keys outside this JSON object.
"""


@dataclass(slots=True)
class OpenAIDailyReportGeneratorConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.4
    # 必要に応じて max_tokens など追加可能


class OpenAIDailyNutritionReportGenerator(DailyNutritionReportGeneratorPort):
    """
    OpenAI Chat Completions API を使って日次栄養レポート文面を生成する実装。

    - OPENAI_API_KEY は環境変数から読み込む前提。
    - JSON モードで summary/good_points/improvement_points/tomorrow_focus を返させる。
    """

    def __init__(
        self,
        client: OpenAI | None = None,
        config: OpenAIDailyReportGeneratorConfig | None = None,
    ) -> None:
        self._client = client or OpenAI()
        self._config = config or OpenAIDailyReportGeneratorConfig()

    # ------------------------------------------------------------------
    # Port 実装
    # ------------------------------------------------------------------

    def generate(self, input: DailyReportLLMInput) -> DailyReportLLMOutput:
        """
        DailyReportLLMInput をもとに LLM に日次レポート生成を依頼する。

        Raises:
            DailyReportGenerationFailedError: 外部 API / JSON パース等の失敗時
        """
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
                "OpenAI API error while generating daily report: user=%s date=%s",
                getattr(input.user_id, "value", input.user_id),
                input.date,
            )
            raise DailyReportGenerationFailedError(
                "Failed to generate daily nutrition report via OpenAI"
            ) from e

        content = completion.choices[0].message.content
        if content is None:
            raise DailyReportGenerationFailedError(
                "OpenAI returned empty content")

        try:
            data: dict[str, Any] = json.loads(content)
        except json.JSONDecodeError as e:
            logger.exception(
                "Failed to parse JSON from daily report response: %s", content)
            raise DailyReportGenerationFailedError(
                "Failed to parse JSON from daily report response"
            ) from e

        try:
            return self._to_output_dto(data)
        except Exception as e:
            logger.exception(
                "Failed to map JSON to DailyReportLLMOutput: %s", data)
            raise DailyReportGenerationFailedError(
                "Failed to map JSON to DailyReportLLMOutput"
            ) from e

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    def _build_user_prompt(self, input: DailyReportLLMInput) -> str:
        """
        DailyReportLLMInput を人間が読める形にまとめて LLM に渡す。
        過度に長くならないよう、要約した情報を渡す。
        """

        profile: Profile = input.profile
        target: DailyTargetSnapshot = input.target_snapshot
        daily: DailyNutritionSummary = input.daily_summary
        meal_summaries: list[MealNutritionSummary] = list(input.meal_summaries)

        lines: list[str] = []

        # --- ユーザープロフィール ------------------------------------
        lines.append(f"User ID: {input.user_id.value}")
        lines.append(f"Date: {input.date.isoformat()}")
        lines.append("")
        lines.append("User profile:")
        lines.append(f"- Sex: {getattr(profile, 'sex', None)}")
        lines.append(f"- Birthdate: {getattr(profile, 'birthdate', None)}")
        lines.append(f"- Height: {getattr(profile, 'height_cm', None)} cm")
        lines.append(f"- Weight: {getattr(profile, 'weight_kg', None)} kg")
        lines.append(
            f"- Meals per day: {getattr(profile, 'meals_per_day', None)}")
        lines.append("")

        # --- 対象日のターゲット概要 ----------------------------------
        lines.append("Daily target snapshot (simplified):")
        lines.append(f"- Goal type: {getattr(target, 'goal_type', None)}")
        lines.append(
            f"- Activity level: {getattr(target, 'activity_level', None)}")
        # 必要であればターゲット栄養素の一部を要約表示
        lines.append("")

        # --- 日次サマリの概要 -----------------------------------------
        lines.append("Daily nutrition summary (simplified):")
        # 例: 主要な栄養素だけ抜き出して載せる（実装に合わせて調整）
        for n in daily.nutrients[:8]:  # とりあえず先頭いくつか
            lines.append(
                f"- {n.code.value}: {n.amount.value} {n.amount.unit} (source={n.source.value})"
            )
        lines.append("")

        # --- Meal ごとの特徴 ------------------------------------------
        lines.append("Meal summaries:")
        for idx, m in enumerate(meal_summaries, start=1):
            lines.append(
                f"Meal {idx}: meal_type={getattr(m, 'meal_type', None)}, "
                f"date={m.date}, "
                f"total nutrients={len(m.nutrients)} items"
            )
        lines.append("")

        lines.append(
            "Based on this information, write a daily nutrition report as JSON "
            "according to the system instructions."
        )

        return "\n".join(lines)

    def _to_output_dto(self, data: dict[str, Any]) -> DailyReportLLMOutput:
        """
        JSON データ -> DailyReportLLMOutput への変換とバリデーション。
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

        summary = _ensure_str(data.get("summary"), "summary")
        good_points = _ensure_str_list(data.get("good_points"), "good_points")
        improvement_points = _ensure_str_list(
            data.get("improvement_points"), "improvement_points"
        )
        tomorrow_focus = _ensure_str_list(
            data.get("tomorrow_focus"), "tomorrow_focus"
        )

        return DailyReportLLMOutput(
            summary=summary,
            good_points=good_points,
            improvement_points=improvement_points,
            tomorrow_focus=tomorrow_focus,
        )
