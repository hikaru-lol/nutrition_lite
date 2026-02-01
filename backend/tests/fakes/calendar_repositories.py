from datetime import date, datetime
from typing import List, Dict
from app.application.calendar.ports.calendar_repository_port import CalendarRepositoryPort
from app.application.calendar.dto.calendar_dto import MonthlyCalendarDto
from app.domain.calendar.entities import CalendarDaySnapshot


class InMemoryCalendarRepository(CalendarRepositoryPort):
    """カレンダーリポジトリのインメモリ実装（テスト用）"""

    def __init__(self) -> None:
        # 食事ログのデータ: (user_id, date) -> bool
        self._meal_logs: Dict[tuple[str, str], bool] = {}

        # 栄養達成度のデータ: (user_id, date) -> int
        self._nutrition_achievements: Dict[tuple[str, str], int] = {}

        # 日次レポートのデータ: (user_id, date) -> bool
        self._daily_reports: Dict[tuple[str, str], bool] = {}

    def clear(self) -> None:
        """テストごとに状態をクリア"""
        self._meal_logs.clear()
        self._nutrition_achievements.clear()
        self._daily_reports.clear()

    def add_meal_log(self, user_id: str, date_str: str, has_meals: bool) -> None:
        """食事ログデータを追加（テスト用）"""
        self._meal_logs[(user_id, date_str)] = has_meals

    def add_nutrition_achievement(self, user_id: str, date_str: str, achievement: int) -> None:
        """栄養達成度データを追加（テスト用）"""
        self._nutrition_achievements[(user_id, date_str)] = achievement

    def add_daily_report(self, user_id: str, date_str: str, has_report: bool) -> None:
        """日次レポートデータを追加（テスト用）"""
        self._daily_reports[(user_id, date_str)] = has_report

    def get_monthly_summary(
        self,
        request: MonthlyCalendarDto
    ) -> List[CalendarDaySnapshot]:
        """指定月の日次スナップショット一覧を取得"""
        # 月の日数を計算
        if request.month == 12:
            next_year = request.year + 1
            next_month = 1
        else:
            next_year = request.year
            next_month = request.month + 1

        start_date = date(request.year, request.month, 1)
        end_date = date(next_year, next_month, 1)

        days = []
        current_date = start_date

        while current_date < end_date:
            date_str = current_date.strftime('%Y-%m-%d')

            # データを取得
            has_meal_logs = self._meal_logs.get((request.user_id, date_str), False)
            nutrition_achievement = self._nutrition_achievements.get((request.user_id, date_str))
            has_daily_report = self._daily_reports.get((request.user_id, date_str), False)

            snapshot = CalendarDaySnapshot(
                date=date_str,
                has_meal_logs=has_meal_logs,
                nutrition_achievement=nutrition_achievement,
                has_daily_report=has_daily_report
            )

            days.append(snapshot)

            # 次の日へ
            if current_date.month == 12 and current_date.day == 31:
                current_date = date(current_date.year + 1, 1, 1)
            elif current_date.month in [1, 3, 5, 7, 8, 10, 12] and current_date.day == 31:
                current_date = date(current_date.year, current_date.month + 1, 1)
            elif current_date.month in [4, 6, 9, 11] and current_date.day == 30:
                current_date = date(current_date.year, current_date.month + 1, 1)
            elif current_date.month == 2:
                # 2月の処理
                is_leap = (current_date.year % 4 == 0 and current_date.year % 100 != 0) or (current_date.year % 400 == 0)
                last_day = 29 if is_leap else 28
                if current_date.day == last_day:
                    current_date = date(current_date.year, 3, 1)
                else:
                    current_date = date(current_date.year, current_date.month, current_date.day + 1)
            else:
                current_date = date(current_date.year, current_date.month, current_date.day + 1)

        return days