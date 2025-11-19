from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .value_objects import EmailAddress, HashedPassword, UserId, UserPlan, TrialInfo


@dataclass
class User:
    """
    認証ドメインの中心となる User エンティティ。
    DDD的には「根幹のビジネスルール」をここに置く。
    """

    id: UserId
    email: EmailAddress
    hashed_password: HashedPassword
    name: str | None
    plan: UserPlan
    trial_info: TrialInfo
    has_profile: bool
    created_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    @property
    def is_active(self) -> bool:
        return self.deleted_at is None

    def mark_deleted(self, deleted_at: datetime | None = None) -> None:
        if self.deleted_at is not None:
            return
        self.deleted_at = deleted_at or datetime.utcnow()
