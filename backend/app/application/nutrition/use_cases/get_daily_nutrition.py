from __future__ import annotations

from datetime import date as DateType

from app.application.nutrition.ports.uow_port import NutritionUnitOfWorkPort
from app.application.auth.ports.plan_checker_port import PlanCheckerPort

from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_nutrition import DailyNutritionSummary


class GetDailyNutritionUseCase:
    """
    指定日の日次栄養サマリを取得するUseCase。

    OpenAI計算は行わず、DBに保存されているデータのみを返す。
    データが存在しない場合はNoneを返す。

    フロー:
      1. (user_id, date) に対応する既存データを検索
      2. 見つかればそのまま返す、なければNone
    """

    def __init__(
        self,
        nutrition_uow: NutritionUnitOfWorkPort,
        plan_checker: PlanCheckerPort,
    ) -> None:
        self._nutrition_uow = nutrition_uow
        self._plan_checker = plan_checker

    def execute(
        self,
        user_id: UserId,
        date_: DateType,
    ) -> DailyNutritionSummary | None:
        # --- 0. プレミアム機能チェック --------------------------------
        self._plan_checker.ensure_premium_feature(user_id)

        # 既存データの検索のみ（OpenAI計算なし）
        with self._nutrition_uow as uow:
            existing = uow.daily_nutrition_repo.get_by_user_and_date(
                user_id=user_id,
                target_date=date_,
            )

            return existing