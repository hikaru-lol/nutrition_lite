from __future__ import annotations

import uuid

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

from app.infra.db.base import Base


class MealRecommendationModel(Base):
    __tablename__ = "meal_recommendations"

    id = sa.Column(
        pg.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    generated_for_date = sa.Column(sa.Date, nullable=False, index=True)
    body = sa.Column(sa.Text, nullable=False)

    # ★DB側default（migrationに合わせる）
    tips = sa.Column(
        pg.ARRAY(sa.Text),
        nullable=False,
        default=list,       # Python側
        server_default="{}",  # DB側（空配列）
    )

    created_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )

    __table_args__ = (
        sa.UniqueConstraint("user_id", "generated_for_date",
                            name="uq_meal_recommendation_user_date"),
    )
