from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.auth.entities import User
from app.domain.auth.value_objects import UserPlan


@dataclass
class AuthUserDTO:
    id: str
    email: str
    name: str | None
    plan: UserPlan
    trial_ends_at: datetime | None
    has_profile: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> "AuthUserDTO":
        return cls(
            id=user.id.value,
            email=user.email.value,
            name=user.name,
            plan=user.plan,
            trial_ends_at=user.trial_info.trial_ends_at,
            has_profile=user.has_profile,
            created_at=user.created_at,
        )
