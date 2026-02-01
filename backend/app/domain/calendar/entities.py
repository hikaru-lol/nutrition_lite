from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CalendarDaySnapshot:
    """カレンダーの1日分のスナップショット"""
    date: str                           # YYYY-MM-DD
    has_meal_logs: bool                # 食事ログ存在フラグ
    nutrition_achievement: Optional[int] # 栄養達成度（0-100%、目標なしならNone）
    has_daily_report: bool             # 日次レポート存在フラグ