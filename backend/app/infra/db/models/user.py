from __future__ import annotations

import uuid

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import Mapped, relationship

from app.infra.db.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.infra.db.models.profile import ProfileModel
    from app.infra.db.models.target import TargetModel
    from app.infra.db.models.billing_account import BillingAccountModel

# relationship("ProfileModel") のままでOK


class UserModel(Base):
    __tablename__ = "users"

    id = sa.Column(
        pg.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email = sa.Column(sa.String, unique=True, index=True, nullable=False)
    hashed_password = sa.Column(sa.String, nullable=False)
    name = sa.Column(sa.String, nullable=True)

    plan = sa.Column(sa.String, nullable=False)  # "trial" / "free" / "paid"
    trial_ends_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    has_profile = sa.Column(sa.Boolean, nullable=False, default=False)

    created_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
    deleted_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    # リレーションシップ
    profile: Mapped["ProfileModel"] = relationship(
        "ProfileModel",
        back_populates="user",
        uselist=False,
    )
    targets: Mapped[list["TargetModel"]] = relationship(
        "TargetModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    billing_account: Mapped["BillingAccountModel"] = relationship(
        "BillingAccountModel",
        back_populates="user",
        uselist=False,
    )
