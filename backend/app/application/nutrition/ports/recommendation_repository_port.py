from __future__ import annotations

from datetime import date
from typing import Protocol, Sequence

from app.domain.auth.value_objects import UserId
from app.domain.nutrition.meal_recommendation import MealRecommendation


class MealRecommendationRepositoryPort(Protocol):
    """
    MealRecommendation の読み書き用ポート。
    """

    def get_by_user_and_date(
        self,
        user_id: UserId,
        generated_for_date: date,
    ) -> MealRecommendation | None:
        ...

    def list_recent_by_user(
        self,
        user_id: UserId,
        limit: int,
    ) -> Sequence[MealRecommendation]:
        ...

    def count_by_user_and_date(
        self,
        user_id: UserId,
        generated_for_date: date,
    ) -> int:
        ...

    def get_latest_by_user(
        self,
        user_id: UserId,
    ) -> MealRecommendation | None:
        ...

    def save(self, recommendation: MealRecommendation) -> None:
        ...
