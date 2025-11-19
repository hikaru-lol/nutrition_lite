from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.domain.auth.value_objects import UserId, UserPlan


@dataclass(frozen=True)
class TokenPayload:
    user_id: str
    plan: UserPlan


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime


class TokenServicePort(Protocol):
    """
    JWT などのトークン発行・検証のためのポート。
    HTTP や Cookie のことは一切知らない。
    """

    def issue_tokens(self, payload: TokenPayload) -> TokenPair:
        ...

    def verify_access_token(self, token: str) -> TokenPayload:
        ...

    def verify_refresh_token(self, token: str) -> TokenPayload:
        ...
