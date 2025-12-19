from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import Mapped, relationship

from app.infra.db.base import Base

if TYPE_CHECKING:
    from app.infra.db.models.user import UserModel


class BillingAccountModel(Base):
    __tablename__ = "billing_accounts"

    id = sa.Column(
        pg.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ★unique/index は付けず、名前付き UniqueConstraint に一本化
    user_id = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    stripe_customer_id = sa.Column(sa.String(255), nullable=True, index=True)
    stripe_subscription_id = sa.Column(
        sa.String(255), nullable=True, index=True)

    # ★DB側default（migrationに合わせる）
    subscription_status = sa.Column(
        sa.String(32),
        nullable=False,
        default="NONE",  # Python側
        server_default=sa.text("'NONE'"),  # DB側
    )

    current_plan = sa.Column(
        sa.String(16),
        nullable=False,
        default="free",  # Python側
        server_default=sa.text("'free'"),  # DB側
    )

    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )

    __table_args__ = (
        sa.UniqueConstraint("user_id", name="uq_billing_account_user_id"),
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="billing_account",
    )
