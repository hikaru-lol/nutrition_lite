from __future__ import annotations

from typing import List
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import relationship

from app.infra.db.base import Base


class DailyNutritionSummaryModel(Base):
    """
    daily_nutrition_summaries テーブル。

    1レコード = あるユーザーの 1日分の栄養サマリ。
    """

    __tablename__ = "daily_nutrition_summaries"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True)

    user_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    date = sa.Column(sa.Date(), nullable=False, index=True)

    generated_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )

    nutrients: List[DailyNutritionNutrientModel] = relationship(
        "DailyNutritionNutrientModel",
        back_populates="summary",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "user_id",
            "date",
            name="uq_daily_nutrition_user_date",
        ),
    )


class DailyNutritionNutrientModel(Base):
    """
    daily_nutrition_nutrients テーブル。

    1レコード = その1日分の中の1栄養素。
    """

    __tablename__ = "daily_nutrition_nutrients"

    summary_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("daily_nutrition_summaries.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # NutrientCode.value
    code = sa.Column(sa.String(length=50), primary_key=True)

    amount_value = sa.Column(sa.Float, nullable=False)
    amount_unit = sa.Column(sa.String(length=20), nullable=False)
    # NutrientSource.value
    source = sa.Column(sa.String(length=50), nullable=False)

    summary = relationship(
        "DailyNutritionSummaryModel",
        back_populates="nutrients",
    )
