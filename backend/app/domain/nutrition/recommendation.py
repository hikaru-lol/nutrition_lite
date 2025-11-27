from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import List
from uuid import UUID, uuid4

from app.domain.auth.value_objects import UserId


@dataclass(frozen=True)
class MealRecommendationId:
    value: UUID

    @classmethod
    def new(cls) -> MealRecommendationId:
        return cls(value=uuid4())


@dataclass
class MealRecommendation:
    """
    食事提案 (Recommendation) のドメインモデル。

    - 「いつのレポート群をもとに生成された提案か」を generated_for_date で表現。
      （例: 直近 5 日分のレポートの最終日など）
    """

    id: MealRecommendationId
    user_id: UserId

    generated_for_date: date  # この日までの履歴をもとにした提案、という意味

    body: str                 # 提案本文（メインテキスト）
    tips: List[str]           # 箇条書きのポイントなど

    created_at: datetime

    @classmethod
    def create(
        cls,
        user_id: UserId,
        generated_for_date: date,
        body: str,
        tips: List[str],
        created_at: datetime,
    ) -> MealRecommendation:
        return cls(
            id=MealRecommendationId.new(),
            user_id=user_id,
            generated_for_date=generated_for_date,
            body=body,
            tips=list(tips),
            created_at=created_at,
        )
