from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Sequence

from app.domain.auth.value_objects import UserId


@dataclass
class DailyLogCompletionResultDTO:
    """
    1 日分の記録完了状態を表す DTO。

    - meals_per_day: Profile に設定されている main meal の回数
    - filled_indices: 記録済みの main meal_index（一意・ソート済み）
    - missing_indices: まだ記録されていない meal_index
    """

    user_id: UserId
    date: date

    meals_per_day: int

    is_completed: bool

    filled_indices: list[int]
    missing_indices: list[int]
