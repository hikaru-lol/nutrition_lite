from __future__ import annotations

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import Mapped, relationship

from app.infra.db.base import Base


class MealNutritionSummaryModel(Base):
    __tablename__ = "meal_nutrition_summaries"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True)

    user_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    date = sa.Column(sa.Date(), nullable=False, index=True)
    meal_type = sa.Column(sa.String(length=16), nullable=False, index=True)
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

    nutrients: Mapped[list["MealNutritionNutrientModel"]] = relationship(
        "MealNutritionNutrientModel",
        back_populates="summary",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        # 既存：meal_index が非NULLならこれで一意性担保
        sa.UniqueConstraint(
            "user_id", "date", "meal_type", "meal_index",
            name="uq_meal_nutrition_user_date_slot",
        ),
        # ★追加：meal_index が NULL の行だけ (user_id, date, meal_type) を一意にする
        sa.Index(
            "uq_meal_nutrition_summaries_user_date_type_null",
            "user_id", "date", "meal_type",
            unique=True,
            postgresql_where=sa.text("meal_index IS NULL"),
        ),
    )


class MealNutritionNutrientModel(Base):
    __tablename__ = "meal_nutrition_nutrients"

    summary_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("meal_nutrition_summaries.id", ondelete="CASCADE"),
        primary_key=True,
    )
    code = sa.Column(sa.String(length=50), primary_key=True)

    amount_value = sa.Column(sa.Float, nullable=False)
    amount_unit = sa.Column(sa.String(length=20), nullable=False)
    source = sa.Column(sa.String(length=50), nullable=False)

    summary: Mapped["MealNutritionSummaryModel"] = relationship(
        "MealNutritionSummaryModel",
        back_populates="nutrients",
    )
