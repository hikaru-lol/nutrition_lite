from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import re

from app.domain.auth.errors import InvalidEmailFormatError


class UserPlan(StrEnum):
    TRIAL = "trial"
    FREE = "free"
    PAID = "paid"


_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        if not _EMAIL_REGEX.match(self.value):
            # 元: raise ValueError(...)
            raise InvalidEmailFormatError(
                f"Invalid email format: {self.value}")


@dataclass(frozen=True)
class HashedPassword:
    """
    ハッシュ済みパスワードを表す VO。
    ・実際のハッシュ処理は PasswordHasherPort 側で行い、
      ここでは「ハッシュ済みである」という意味だけを持つ。
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("HashedPassword cannot be empty")


@dataclass(frozen=True)
class UserId:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("UserId cannot be empty")


@dataclass(frozen=True)
class TrialInfo:
    trial_ends_at: datetime | None

    def is_trial_active(self, now: datetime) -> bool:
        if self.trial_ends_at is None:
            return False
        return now < self.trial_ends_at
