from abc import ABC, abstractmethod
from typing import List
from app.domain.calendar.entities import CalendarDaySnapshot
from app.application.calendar.dto.calendar_dto import MonthlyCalendarDto


class CalendarRepositoryPort(ABC):
    """カレンダーリポジトリのポート（インターフェース）"""

    @abstractmethod
    def get_monthly_summary(
        self,
        request: MonthlyCalendarDto
    ) -> List[CalendarDaySnapshot]:
        """指定月の日次スナップショット一覧を取得"""
        pass
