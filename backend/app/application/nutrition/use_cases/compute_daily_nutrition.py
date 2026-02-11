from __future__ import annotations

from collections import defaultdict
from datetime import date as DateType
from typing import Sequence

from app.application.auth.ports.plan_checker_port import PlanCheckerPort
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.meal_nutrition import MealNutritionSummary
from app.domain.nutrition.daily_nutrition import (
    DailyNutritionSummary,
)
from app.domain.target.value_objects import NutrientCode, NutrientAmount, NutrientSource
from app.application.nutrition.ports.uow_port import NutritionUnitOfWorkPort


class ComputeDailyNutritionSummaryUseCase:
    """
    1日分の栄養サマリ (DailyNutritionSummary) を計算し、DB に保存する UseCase。

    - 入力:
        user_id, date
    - 処理:
        1. その日の MealNutritionSummary 一覧を取得
        2. NutrientCode ごとに amount.value を合計
        3. DailyNutritionSummary を組み立て
        4. 既存サマリがあれば上書き、なければ新規作成
    - 出力:
        最新の DailyNutritionSummary

    追加: プレミアム機能チェック
      - trial / paid のユーザーのみ実行可能。
      - FREE の場合は PremiumFeatureRequiredError を投げる。
    """

    def __init__(
        self,
        uow: NutritionUnitOfWorkPort,
        plan_checker: PlanCheckerPort,
    ) -> None:
        self._uow = uow
        self._plan_checker = plan_checker

    def execute(self, user_id: UserId, date_: DateType) -> DailyNutritionSummary:
        # --- 0. プレミアム機能チェック --------------------------------
        self._plan_checker.ensure_premium_feature(user_id)

        with self._uow as uow:
            meals: Sequence[MealNutritionSummary] = uow.meal_nutrition_repo.list_by_user_and_date(
                user_id=user_id,
                target_date=date_,
            )

            totals: dict[NutrientCode, float] = defaultdict(float)
            unit_map: dict[NutrientCode, str] = {}

            for meal in meals:
                for n in meal.nutrients:
                    totals[n.code] += n.amount.value
                    unit_map.setdefault(n.code, n.amount.unit)

            pairs: list[tuple[NutrientCode, NutrientAmount]] = [
                (code, NutrientAmount(value=value, unit=unit_map[code]))
                for code, value in totals.items()
            ]

            existing = uow.daily_nutrition_repo.get_by_user_and_date(
                user_id=user_id,
                target_date=date_,
            )
            summary_id = existing.id if existing is not None else None
            source = NutrientSource("llm")

            summary = DailyNutritionSummary.from_nutrient_amounts(
                user_id=user_id,
                date=date_,
                nutrients=pairs,
                source=source,
                summary_id=summary_id,
            )

            uow.daily_nutrition_repo.save(summary)

            return summary
