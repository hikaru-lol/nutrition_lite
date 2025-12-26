from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List
from uuid import UUID, uuid4

from app.domain.auth.value_objects import UserId


@dataclass(frozen=True)
class DailyNutritionReportId:
    value: UUID

    @classmethod
    def new(cls) -> DailyNutritionReportId:
        return cls(value=uuid4())


@dataclass
class DailyNutritionReport:
    id: DailyNutritionReportId
    user_id: UserId
    date: date

    summary: str

    good_points: List[str] = field(default_factory=list)
    improvement_points: List[str] = field(default_factory=list)
    tomorrow_focus: List[str] = field(default_factory=list)

    # ✅ keyword-only にして「default引数の後ろに必須引数」が来てもOKにする
    created_at: datetime = field(kw_only=True)

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
