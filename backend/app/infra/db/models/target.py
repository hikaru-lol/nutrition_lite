from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.infra.db.base import Base


class TargetModel(Base):
    """
    targets テーブルの SQLAlchemy モデル。

    - 1レコードが 1 つの TargetDefinition に対応する。
    """

    __tablename__ = "targets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String, nullable=False)
    goal_type = Column(String, nullable=False)         # GoalType の value
    goal_description = Column(String, nullable=True)
    activity_level = Column(String, nullable=False)    # ActivityLevel の value

    is_active = Column(Boolean, nullable=False, default=False)

    llm_rationale = Column(String, nullable=True)
    disclaimer = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    # 1:多 の関係 - TargetNutrientModel
    nutrients = relationship(
        "TargetNutrientModel",
        back_populates="target",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    __table_args__ = (
        # 1ユーザーにつき最大1アクティブにするための制約はアプリ側で担保する。
        # 必要なら部分索引や CHECK 制約も検討。
    )


class TargetNutrientModel(Base):
    """
    target_nutrients テーブル。

    - 1つの TargetDefinition に対する 17 種の栄養素ごとのターゲット値。
    """

    __tablename__ = "target_nutrients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_id = Column(
        UUID(as_uuid=True),
        ForeignKey("targets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    code = Column(String, nullable=False)   # NutrientCode の value
    amount = Column(Float, nullable=False)
    unit = Column(String, nullable=False)   # g, mg, µg, kcal, etc.
    source = Column(String, nullable=False)  # "llm" / "manual" / "user_input"

    target = relationship("TargetModel", back_populates="nutrients")

    __table_args__ = (
        UniqueConstraint("target_id", "code",
                         name="uq_target_nutrient_code_per_target"),
    )


class DailyTargetSnapshotModel(Base):
    """
    daily_target_snapshots テーブル。

    - 特定ユーザーの特定日付に対して確定されたターゲットスナップショット。
    - 過去日のみ作成し、以後更新しない想定。
    """

    __tablename__ = "daily_target_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)

    # どの TargetDefinition からコピーされたか
    target_id = Column(
        UUID(as_uuid=True),
        ForeignKey("targets.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at = Column(DateTime(timezone=True), nullable=False)

    # 1:多 の関係 - DailyTargetSnapshotNutrientModel
    nutrients = relationship(
        "DailyTargetSnapshotNutrientModel",
        back_populates="snapshot",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_snapshot_user_date"),
    )


class DailyTargetSnapshotNutrientModel(Base):
    """
    daily_target_snapshot_nutrients テーブル。

    - DailyTargetSnapshot ごとの 17 栄養素のスナップショット値。
    """

    __tablename__ = "daily_target_snapshot_nutrients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_id = Column(
        UUID(as_uuid=True),
        ForeignKey("daily_target_snapshots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    code = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    source = Column(String, nullable=False)

    snapshot = relationship("DailyTargetSnapshotModel",
                            back_populates="nutrients")

    __table_args__ = (
        UniqueConstraint("snapshot_id", "code",
                         name="uq_snapshot_nutrient_code_per_snapshot"),
    )
