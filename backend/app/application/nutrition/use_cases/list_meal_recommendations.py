from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.application.auth.ports.plan_checker_port import PlanCheckerPort
from app.application.nutrition.ports.uow_port import NutritionUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.meal_recommendation import MealRecommendation


@dataclass(slots=True)
class ListMealRecommendationsInput:
    """
    提案リスト取得 UC の入力。
    """

    user_id: UserId
    limit: int = 20


class ListMealRecommendationsUseCase:
    """
    指定ユーザーの MealRecommendation を作成日時の新しい順に取得する UseCase。
    """

    def __init__(
        self,
        nutrition_uow: NutritionUnitOfWorkPort,
        plan_checker: PlanCheckerPort | None = None,
    ) -> None:
        self._nutrition_uow = nutrition_uow
        self._plan_checker = plan_checker

    def execute(self, input: ListMealRecommendationsInput) -> Sequence[MealRecommendation]:
        # --- プレミアム機能チェック --------------------------------
        if self._plan_checker:
            self._plan_checker.ensure_premium_feature(input.user_id)

        # --- 提案リスト取得 --------------------------------------
        with self._nutrition_uow as uow:
            return uow.meal_recommendation_repo.list_recent_by_user(
                user_id=input.user_id,
                limit=input.limit,
            )