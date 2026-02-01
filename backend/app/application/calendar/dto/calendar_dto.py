from dataclasses import dataclass
from typing import List
from app.domain.calendar.entities import CalendarDaySnapshot


@dataclass(frozen=True)
class MonthlyCalendarDto:
    """月次カレンダー取得リクエスト"""
    user_id: str
    year: int
    month: int


@dataclass(frozen=True)
class MonthlyCalendarResultDto:
    """月次カレンダー取得結果"""
    year: int
    month: int
    days: List[CalendarDaySnapshot]
