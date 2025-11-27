from __future__ import annotations

from datetime import date
from typing import Protocol, Sequence

from app.domain.auth.value_objects import UserId
from app.domain.nutrition.recommendation import MealRecommendation


class MealRecommendationRepositoryPort(Protocol):
    """
    MealRecommendation 用 Repository ポート。
    """

    def get_by_user_and_date(
        self,
        user_id: UserId,
        generated_for_date: date,
    ) -> MealRecommendation | None:
        """
        指定した (user_id, generated_for_date) の提案を 0 または 1 件返す。
        """
        raise NotImplementedError

    def list_recent(
        self,
        user_id: UserId,
        limit: int,
    ) -> Sequence[MealRecommendation]:
        """
        ユーザーの提案を新しい順に取得。
        """
        raise NotImplementedError

    def save(self, recommendation: MealRecommendation) -> None:
        """
        提案を新規作成 or 更新として保存。
        """
        raise NotImplementedError
