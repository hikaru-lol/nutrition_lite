from __future__ import annotations

from typing import Protocol

from app.application.nutrition.dto.daily_report_llm_dto import (
    DailyReportLLMInput,
    DailyReportLLMOutput,
)


class DailyNutritionReportGeneratorPort(Protocol):
    """
    日次栄養レポートを生成するための LLM ポート。

    - 実装例:
        - StubDailyNutritionReportGenerator
        - OpenAIDailyNutritionReportGenerator
    """

    def generate(self, input: DailyReportLLMInput) -> DailyReportLLMOutput:
        """
        Profile / Target / Daily / Meal 情報をもとに、
        1 日分のレポート（summary / good / improvement / tomorrow_focus）を生成する。
        """
        raise NotImplementedError
