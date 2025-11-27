from __future__ import annotations

from datetime import date
from typing import Protocol, Sequence

from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_report import DailyNutritionReport


class DailyNutritionReportRepositoryPort(Protocol):
    """
    DailyNutritionReport 用の Repository ポート。

    - DDD 的には「読み書きの窓口」として Application 層から利用する。
    """

    def get_by_user_and_date(
        self,
        user_id: UserId,
        target_date: date,
    ) -> DailyNutritionReport | None:
        """
        指定した (user_id, date) のレポートを 0 または 1 件返す。
        """
        raise NotImplementedError

    def list_recent(
        self,
        user_id: UserId,
        limit: int,
    ) -> Sequence[DailyNutritionReport]:
        """
        ユーザーごとの直近レポートを新しい順に返す。

        - 提案機能で「直近 5 日分のレポート」を取得する用途などを想定。
        """
        raise NotImplementedError

    def save(self, report: DailyNutritionReport) -> None:
        """
        レポートを新規作成または更新として保存する。

        - 実装側では id の有無や状態に応じて insert/update を行う。
        """
        raise NotImplementedError
