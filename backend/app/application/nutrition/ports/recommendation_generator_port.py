from __future__ import annotations

from typing import Protocol

from app.application.nutrition.dto.meal_recommendation_llm_dto import (
    MealRecommendationLLMInput,
    MealRecommendationLLMOutput,
)


class MealRecommendationGeneratorPort(Protocol):
    """
    MealRecommendation を LLM などで生成するポート。
    """

    def generate(
        self,
        input: MealRecommendationLLMInput,
    ) -> MealRecommendationLLMOutput:
        ...
