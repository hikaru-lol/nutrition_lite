from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from app.domain.auth.value_objects import UserId


@dataclass(slots=True)
class MealRecommendationId:
    value: str

    @classmethod
    def new(cls) -> MealRecommendationId:
        from uuid import uuid4
        return cls(value=str(uuid4()))


@dataclass(slots=True)
class MealRecommendation:
    """
    1ユーザー・1日あたり高々1件の「提案」エンティティ。
    """

    id: MealRecommendationId
    user_id: UserId
    generated_for_date: date  # この日までの履歴をもとにした提案

    body: str                 # メインの提案文
    tips: list[str]           # 実行可能なアクション（箇条書き）

    created_at: datetime

    @classmethod
    def create(
        cls,
        user_id: UserId,
        generated_for_date: date,
        body: str,
        tips: list[str],
        created_at: datetime,
    ) -> MealRecommendation:
        return cls(
            id=MealRecommendationId.new(),
            user_id=user_id,
            generated_for_date=generated_for_date,
            body=body,
            tips=tips,
            created_at=created_at,
        )
