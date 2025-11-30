from __future__ import annotations

from datetime import date as DateType

from app.application.nutrition.ports.uow_port import NutritionUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_report import DailyNutritionReport


class GetDailyNutritionReportUseCase:
    """
    指定した (user_id, date) の DailyNutritionReport を取得する UseCase。

    - 既に生成済みのレポートを読むだけ。
    - 存在しない場合は None を返す。
      （HTTP の 404 へのマッピングは API 層で行う）
    """

    def __init__(self, uow: NutritionUnitOfWorkPort) -> None:
        self._uow = uow

    def execute(
        self,
        user_id: UserId,
        date_: DateType,
    ) -> DailyNutritionReport | None:
        with self._uow as uow:
            return uow.daily_report_repo.get_by_user_and_date(
                user_id=user_id,
                target_date=date_,
            )
