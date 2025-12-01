from __future__ import annotations

from typing import Protocol

from app.application.nutrition.dto.recommendation_llm_dto import (
    MealRecommendationLLMInput,
    MealRecommendationLLMOutput,
)


class MealRecommendationGeneratorPort(Protocol):
    """
    食事提案 (Recommendation) を生成するための LLM ポート。
    """

    def generate(self, input: MealRecommendationLLMInput) -> MealRecommendationLLMOutput:
        raise NotImplementedError
