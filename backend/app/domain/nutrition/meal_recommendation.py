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


@dataclass(slots=True, frozen=True)
class RecommendedMeal:
    """推奨される具体的な献立"""
    title: str              # 献立名（例：「高タンパク朝食セット」）
    description: str        # 献立の詳細説明と栄養価の特徴
    ingredients: list[str]  # 主要な食材・料理名のリスト
    nutrition_focus: str    # この献立の栄養的なメリット


@dataclass(slots=True)
class MealRecommendation:
    """
    1ユーザー・1日あたり高々1件の「提案」エンティティ。
    """

    id: MealRecommendationId
    user_id: UserId
    generated_for_date: date  # この日までの履歴をもとにした提案

    body: str                           # メインの提案文
    tips: list[str]                     # 実行可能なアクション（箇条書き）
    recommended_meals: list[RecommendedMeal]  # 推奨する具体的な献立3品

    created_at: datetime

    @classmethod
    def create(
        cls,
        user_id: UserId,
        generated_for_date: date,
        body: str,
        tips: list[str],
        recommended_meals: list[RecommendedMeal],
        created_at: datetime,
    ) -> MealRecommendation:
        return cls(
            id=MealRecommendationId.new(),
            user_id=user_id,
            generated_for_date=generated_for_date,
            body=body,
            tips=tips,
            recommended_meals=recommended_meals,
            created_at=created_at,
        )
