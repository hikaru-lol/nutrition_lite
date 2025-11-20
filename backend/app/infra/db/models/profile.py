from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Float, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.infra.db.base import Base


class ProfileModel(Base):
    """
    profiles テーブルの SQLAlchemy モデル。

    - User と 1:1 で紐づく（user_id が PK & users.id の FK）
    """

    __tablename__ = "profiles"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    sex = Column(String, nullable=False)
    birthdate = Column(Date, nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)

    image_id = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
