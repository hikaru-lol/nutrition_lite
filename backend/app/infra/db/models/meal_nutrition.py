from __future__ import annotations

from typing import List
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import relationship

from app.infra.db.base import Base


class MealNutritionSummaryModel(Base):
    """
    meal_nutrition_summaries テーブル。

    1レコード = 1食分の栄養サマリ。
    """

    __tablename__ = "meal_nutrition_summaries"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True)

    user_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    date = sa.Column(sa.Date(), nullable=False, index=True)

    # "main" or "snack"
    meal_type = sa.Column(sa.String(length=16), nullable=False, index=True)

    # main: 1..N / snack: NULL
    meal_index = sa.Column(sa.SmallInteger(), nullable=True)

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

    nutrients: List[MealNutritionNutrientModel] = relationship(
        "MealNutritionNutrientModel",
        back_populates="summary",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "user_id",
            "date",
            "meal_type",
            "meal_index",
            name="uq_meal_nutrition_user_date_slot",
        ),
    )


class MealNutritionNutrientModel(Base):
    """
    meal_nutrition_nutrients テーブル。

    1レコード = ある1食分の中の1栄養素分。
    """

    __tablename__ = "meal_nutrition_nutrients"

    summary_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("meal_nutrition_summaries.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # NutrientCode.value
    code = sa.Column(sa.String(length=50), primary_key=True)

    amount_value = sa.Column(sa.Float, nullable=False)
    amount_unit = sa.Column(sa.String(length=20), nullable=False)
    # NutrientSource.value
    source = sa.Column(sa.String(length=50), nullable=False)

    summary = relationship(
        "MealNutritionSummaryModel",
        back_populates="nutrients",
    )
