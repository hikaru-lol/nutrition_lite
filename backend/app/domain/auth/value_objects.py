from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import re


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
            raise ValueError(f"Invalid email format: {self.value}")


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
    """
    トライアル期間に関する情報。
    """

    trial_ends_at: datetime | None

    @property
    def is_trial_active(self) -> bool:
        if self.trial_ends_at is None:
            return False
        return datetime.utcnow() < self.trial_ends_at
