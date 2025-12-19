from __future__ import annotations

from uuid import uuid4
from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import Mapped, relationship

from app.infra.db.base import Base

if TYPE_CHECKING:
    from app.infra.db.models.user import UserModel


class TargetModel(Base):
    __tablename__ = "targets"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid4)

    user_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = sa.Column(sa.String(length=255), nullable=False)
    goal_type = sa.Column(sa.String(length=50), nullable=False)
    goal_description = sa.Column(sa.Text, nullable=True)
    activity_level = sa.Column(sa.String(length=50), nullable=False)

    # ★DB側default（migrationに合わせる）
    is_active = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,  # Python側
        server_default=sa.text("false"),  # DB側
        index=True,
    )

    llm_rationale = sa.Column(sa.Text, nullable=True)
    disclaimer = sa.Column(sa.Text, nullable=True)

    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
    updated_at = sa.Column(sa.DateTime(timezone=True), nullable=False)

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="targets",
    )

    nutrients: Mapped[list["TargetNutrientModel"]] = relationship(
        "TargetNutrientModel",
        back_populates="target",
        cascade="all, delete-orphan",
        order_by="TargetNutrientModel.code",
    )


class TargetNutrientModel(Base):
    __tablename__ = "target_nutrients"

    target_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("targets.id", ondelete="CASCADE"),
        primary_key=True,
    )
    code = sa.Column(sa.String(length=50), primary_key=True)

    amount_value = sa.Column(sa.Float, nullable=False)
    amount_unit = sa.Column(sa.String(length=20), nullable=False)
    source = sa.Column(sa.String(length=20), nullable=False)

    target: Mapped["TargetModel"] = relationship(
        "TargetModel",
        back_populates="nutrients",
    )


class DailyTargetSnapshotModel(Base):
    __tablename__ = "daily_target_snapshots"

    id = sa.Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid4)

    user_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    date = sa.Column(sa.Date, nullable=False, index=True)

    # ★SET NULL と整合させる（migrationに合わせる）
    target_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("targets.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False)

    __table_args__ = (
        sa.UniqueConstraint("user_id", "date",
                            name="uq_daily_target_snapshot_user_date"),
    )

    nutrients: Mapped[list["DailyTargetSnapshotNutrientModel"]] = relationship(
        "DailyTargetSnapshotNutrientModel",
        back_populates="snapshot",
        cascade="all, delete-orphan",
        order_by="DailyTargetSnapshotNutrientModel.code",
    )


class DailyTargetSnapshotNutrientModel(Base):
    __tablename__ = "daily_target_snapshot_nutrients"

    snapshot_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("daily_target_snapshots.id", ondelete="CASCADE"),
        primary_key=True,
    )
    code = sa.Column(sa.String(length=50), primary_key=True)

    amount_value = sa.Column(sa.Float, nullable=False)
    amount_unit = sa.Column(sa.String(length=20), nullable=False)
    source = sa.Column(sa.String(length=20), nullable=False)

    snapshot: Mapped["DailyTargetSnapshotModel"] = relationship(
        "DailyTargetSnapshotModel",
        back_populates="nutrients",
    )
