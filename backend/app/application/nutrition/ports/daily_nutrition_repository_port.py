from __future__ import annotations

from datetime import date
from typing import Protocol, Sequence

from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_nutrition import DailyNutritionSummary


class DailyNutritionSummaryRepositoryPort(Protocol):
    """
    DailyNutritionSummary の永続化・取得用の Port。
    """

    def get_by_user_and_date(
        self,
        *,
        user_id: UserId,
        target_date: date,
    ) -> DailyNutritionSummary | None:
        """
        指定ユーザーの、指定日付のサマリを1件返す。なければ None。
        """
        ...

    def list_by_user_and_range(
        self,
        *,
        user_id: UserId,
        start_date: date,
        end_date: date,
    ) -> Sequence[DailyNutritionSummary]:
        """
        指定ユーザーの、指定範囲の日付に対するサマリ一覧を返す。
        （将来の週次・月次レポートなどで利用）
        """
        ...

    def save(self, summary: DailyNutritionSummary) -> None:
        """
        DailyNutritionSummary を保存する。

        - summary.id が既存レコードと一致する場合は update
        - なければ insert
        """
        ...
