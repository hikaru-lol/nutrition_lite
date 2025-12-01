from __future__ import annotations

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

from app.infra.db.base import Base


class FoodEntryModel(Base):
    """
    1品分の食事ログ。

    - 物理テーブル: food_entries
    """

    __tablename__ = "food_entries"

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

    # main のとき: 1..N / snack のとき: NULL
    meal_index = sa.Column(sa.SmallInteger(), nullable=True)

    name = sa.Column(sa.String(length=255), nullable=False)

    amount_value = sa.Column(sa.Float, nullable=True)
    amount_unit = sa.Column(sa.String(length=32), nullable=True)
    serving_count = sa.Column(sa.Float, nullable=True)

    note = sa.Column(sa.Text(), nullable=True)

    created_at = sa.Column(
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
    deleted_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=True,
        index=True,
    )
