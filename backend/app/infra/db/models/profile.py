from __future__ import annotations

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import Mapped, relationship

from app.infra.db.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.infra.db.models.user import UserModel


class ProfileModel(Base):
    """
    profiles テーブルの SQLAlchemy モデル。

    - User と 1:1 で紐づく（user_id が PK & users.id の FK）
    """

    __tablename__ = "profiles"

    user_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    sex = sa.Column(sa.String, nullable=False)
    birthdate = sa.Column(sa.Date, nullable=False)
    height_cm = sa.Column(sa.Float, nullable=False)
    weight_kg = sa.Column(sa.Float, nullable=False)

    image_id = sa.Column(sa.String, nullable=True)

    meals_per_day = sa.Column(sa.SmallInteger, nullable=True)

    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
    updated_at = sa.Column(sa.DateTime(timezone=True), nullable=False)

    # リレーションシップ
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="profile",
    )
