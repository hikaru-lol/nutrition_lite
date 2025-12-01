from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List
from uuid import UUID, uuid4

from app.domain.auth.value_objects import UserId


@dataclass(frozen=True)
class DailyNutritionReportId:
    """
    DailyNutritionReport 用の ID 値オブジェクト。
    """

    value: UUID

    @classmethod
    def new(cls) -> DailyNutritionReportId:
        return cls(value=uuid4())


@dataclass
class DailyNutritionReport:
    """
    1 日分の栄養レポート。

    - user_id + date ごとに 0 or 1 件を想定。
    """

    id: DailyNutritionReportId
    user_id: UserId
    date: date

    # --- レポート内容（LLM から生成される部分） ----------------------

    summary: str  # その日の総評（短めの本文）

    good_points: List[str] = field(default_factory=list)
    improvement_points: List[str] = field(default_factory=list)
    tomorrow_focus: List[str] = field(default_factory=list)

    # --- メタ情報 -----------------------------------------------------

    created_at: datetime

    @classmethod
    def create(
        cls,
        user_id: UserId,
        date: date,
        summary: str,
        good_points: List[str],
        improvement_points: List[str],
        tomorrow_focus: List[str],
        created_at: datetime,
    ) -> DailyNutritionReport:
        """
        新規レポート作成用のファクトリ。

        - id はここで自動採番。
        """
        return cls(
            id=DailyNutritionReportId.new(),
            user_id=user_id,
            date=date,
            summary=summary,
            good_points=list(good_points),
            improvement_points=list(improvement_points),
            tomorrow_focus=list(tomorrow_focus),
            created_at=created_at,
        )
