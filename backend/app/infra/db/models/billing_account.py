from __future__ import annotations

import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.infra.db.base import Base


class BillingAccountModel(Base):
    """
    BillingAccount 用の SQLAlchemy モデル。

    - 1ユーザーにつき 1 レコード（user_id に unique 制約）。
    """

    __tablename__ = "billing_accounts"

    id = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,   # 1ユーザー1アカウント
        index=True,
    )

    # Stripe 連携用
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True, index=True)

    # サブスクリプション状態（文字列化した BillingSubscriptionStatus）
    subscription_status = Column(
        String(32), nullable=False, default="NONE")

    # 論理プラン（UserPlan と同期: "trial" / "free" / "paid"）
    current_plan = Column(String(16), nullable=False, default="free")

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_billing_account_user_id"),
    )
