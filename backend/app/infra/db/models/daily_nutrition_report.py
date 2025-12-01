from __future__ import annotations

from datetime import datetime, date
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base  # プロジェクトで使っている Base に合わせて調整


class DailyNutritionReportModel(Base):
    """
    DailyNutritionReport の永続化モデル。

    - (user_id, date) で一意。
    """

    __tablename__ = "daily_nutrition_reports"

    id: Mapped[pg.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    user_id: Mapped[pg.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    date: Mapped[date] = mapped_column(sa.Date, nullable=False, index=True)

    summary: Mapped[str] = mapped_column(sa.Text, nullable=False)

    # TEXT[] として保存（PostgreSQL 前提）
    good_points: Mapped[list[str]] = mapped_column(
        pg.ARRAY(sa.Text),
        nullable=False,
        server_default="{}",
    )
    improvement_points: Mapped[list[str]] = mapped_column(
        pg.ARRAY(sa.Text),
        nullable=False,
        server_default="{}",
    )
    tomorrow_focus: Mapped[list[str]] = mapped_column(
        pg.ARRAY(sa.Text),
        nullable=False,
        server_default="{}",
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "user_id",
            "date",
            name="uq_daily_nutrition_reports_user_id_date",
        ),
    )
