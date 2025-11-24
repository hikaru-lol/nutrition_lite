from __future__ import annotations

from datetime import datetime, date
from uuid import uuid4

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import Mapped, relationship  # ★ Mapped を追加

from app.infra.db.base import Base  # プロジェクトの Base に合わせて調整


class TargetModel(Base):
    """
    TargetDefinition に対応するテーブル。

    - 1 ユーザーは複数の Target を持てる
    - nutrients は TargetNutrientModel で別テーブル管理
    """

    __tablename__ = "targets"

    id = sa.Column(
        pg.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = sa.Column(sa.String(length=255), nullable=False)
    goal_type = sa.Column(sa.String(length=50),
                          nullable=False)       # GoalType.value
    goal_description = sa.Column(sa.Text, nullable=True)
    activity_level = sa.Column(
        sa.String(length=50), nullable=False)  # ActivityLevel.value

    is_active = sa.Column(sa.Boolean, nullable=False,
                          default=False, index=True)

    llm_rationale = sa.Column(sa.Text, nullable=True)
    disclaimer = sa.Column(sa.Text, nullable=True)

    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
    updated_at = sa.Column(sa.DateTime(timezone=True), nullable=False)

    # nutrients との 1:N 関係
    # ★ 型を Mapped[...] に変更
    nutrients: Mapped[list["TargetNutrientModel"]] = relationship(
        "TargetNutrientModel",
        back_populates="target",
        cascade="all, delete-orphan",
        order_by="TargetNutrientModel.code",
    )


class TargetNutrientModel(Base):
    """
    TargetDefinition の 1 栄養素分。

    - (target_id, code) で一意になる想定。
    """

    __tablename__ = "target_nutrients"

    target_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("targets.id", ondelete="CASCADE"),
        primary_key=True,
    )
    # NutrientCode.value
    code = sa.Column(sa.String(length=50), primary_key=True)

    amount_value = sa.Column(sa.Float, nullable=False)  # NutrientAmount.value
    amount_unit = sa.Column(sa.String(length=20),
                            nullable=False)  # NutrientAmount.unit
    # NutrientSource.value
    source = sa.Column(sa.String(length=20), nullable=False)

    # ★ 型を Mapped[...] に変更
    target: Mapped["TargetModel"] = relationship(
        "TargetModel",
        back_populates="nutrients",
    )


class DailyTargetSnapshotModel(Base):
    """
    DailyTargetSnapshot に対応するテーブル。

    - id は内部用のサロゲートキー
    - (user_id, date) はユニーク制約（1日1スナップショット）
    """

    __tablename__ = "daily_target_snapshots"

    id = sa.Column(
        pg.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date = sa.Column(sa.Date, nullable=False, index=True)
    target_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("targets.id", ondelete="SET NULL"),
        nullable=False,
    )

    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False)

    __table_args__ = (
        sa.UniqueConstraint(
            "user_id",
            "date",
            name="uq_daily_target_snapshot_user_date",
        ),
    )

    # ★ 型を Mapped[...] に変更
    nutrients: Mapped[list["DailyTargetSnapshotNutrientModel"]] = relationship(
        "DailyTargetSnapshotNutrientModel",
        back_populates="snapshot",
        cascade="all, delete-orphan",
        order_by="DailyTargetSnapshotNutrientModel.code",
    )


class DailyTargetSnapshotNutrientModel(Base):
    """
    DailyTargetSnapshot の時点の栄養素情報。

    - (snapshot_id, code) で一意。
    """

    __tablename__ = "daily_target_snapshot_nutrients"

    snapshot_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("daily_target_snapshots.id", ondelete="CASCADE"),
        primary_key=True,
    )
    # NutrientCode.value
    code = sa.Column(sa.String(length=50), primary_key=True)

    amount_value = sa.Column(sa.Float, nullable=False)
    amount_unit = sa.Column(sa.String(length=20), nullable=False)
    source = sa.Column(sa.String(length=20), nullable=False)

    # ★ 型を Mapped[...] に変更
    snapshot: Mapped["DailyTargetSnapshotModel"] = relationship(
        "DailyTargetSnapshotModel",
        back_populates="nutrients",
    )
