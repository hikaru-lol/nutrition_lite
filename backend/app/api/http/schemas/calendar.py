from pydantic import BaseModel, Field
from typing import List, Optional


class CalendarDaySnapshotSchema(BaseModel):
    """カレンダー日次スナップショットスキーマ"""
    date: str
    has_meal_logs: bool
    nutrition_achievement: Optional[int]
    has_daily_report: bool


class MonthlyCalendarQuerySchema(BaseModel):
    """月次カレンダークエリパラメータ"""
    year: int = Field(..., ge=2000, le=3000, description="年（2000-3000）")
    month: int = Field(..., ge=1, le=12, description="月（1-12）")


class MonthlyCalendarResponseSchema(BaseModel):
    """月次カレンダーレスポンス"""
    year: int
    month: int
    days: List[CalendarDaySnapshotSchema]