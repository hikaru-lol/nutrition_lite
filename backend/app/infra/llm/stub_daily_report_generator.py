from __future__ import annotations

from app.application.nutrition.dto.daily_report_llm_dto import (
    DailyReportLLMInput,
    DailyReportLLMOutput,
)
from app.application.nutrition.ports.daily_report_generator_port import (
    DailyNutritionReportGeneratorPort,
)


class StubDailyNutritionReportGenerator(DailyNutritionReportGeneratorPort):
    """
    開発・テスト用のスタブ実装。

    - 毎回同じようなテキストを返すだけ。
    - LLM 連携前の動作確認用。
    """

    def generate(self, input: DailyReportLLMInput) -> DailyReportLLMOutput:
        # ここでは input をほぼ無視して固定文言＋日付くらいだけ使う
        date_str = input.date.isoformat()

        summary = f"{date_str} の食事は、全体としてバランスよく摂取できました。"
        good = [
            "たんぱく質を十分に摂取できています。",
            "野菜・果物からのビタミン・ミネラルが取れています。",
        ]
        improvement = [
            "水分摂取量がやや少ない可能性があります。",
            "脂質の質（飽和脂肪酸 / 不飽和脂肪酸）に少し注意してみましょう。",
        ]
        tomorrow = [
            "朝食でたんぱく質を意識的に摂る。",
            "1 日を通してこまめに水分補給する。",
        ]

        return DailyReportLLMOutput(
            summary=summary,
            good_points=good,
            improvement_points=improvement,
            tomorrow_focus=tomorrow,
        )
