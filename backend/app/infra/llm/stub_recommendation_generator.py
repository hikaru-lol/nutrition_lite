from __future__ import annotations

from app.application.nutrition.dto.recommendation_llm_dto import (
    MealRecommendationLLMInput,
    MealRecommendationLLMOutput,
)
from app.application.nutrition.ports.recommendation_generator_port import (
    MealRecommendationGeneratorPort,
)


class StubMealRecommendationGenerator(MealRecommendationGeneratorPort):
    """
    開発・テスト用のスタブ実装。

    - recent_reports を軽く見てテキストをでっちあげるだけ。
    """

    def generate(self, input: MealRecommendationLLMInput) -> MealRecommendationLLMOutput:
        base_date_str = input.base_date.isoformat()
        days = len(input.recent_reports)

        body = (
            f"直近 {days} 日分（〜{base_date_str}）の食事傾向をもとに、"
            "次の食事の方針を簡単にまとめました。"
        )
        tips = [
            "毎食ごとにたんぱく質源（肉・魚・卵・大豆製品など）を 1 品入れてみましょう。",
            "野菜・海藻・きのこを 1 日 2 回以上は意識して取り入れてみてください。",
            "甘い飲み物やお菓子をとる場合は、時間帯や頻度を決めてメリハリをつけましょう。",
        ]

        return MealRecommendationLLMOutput(
            body=body,
            tips=tips,
        )
