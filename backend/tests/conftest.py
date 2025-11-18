from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from fastapi.testclient import TestClient
from app.main import create_app

import pytest

from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.application.auth.ports.password_hasher_port import PasswordHasherPort
from app.application.auth.ports.token_service_port import (
    TokenServicePort,
    TokenPair,
    TokenPayload,
)
from app.application.auth.ports.clock_port import ClockPort
from app.domain.auth.entities import User
from app.domain.auth.value_objects import (
    EmailAddress,
    HashedPassword,
    TrialInfo,
    UserId,
    UserPlan,
)


# ---------- Fake 実装 ----------

class InMemoryUserRepository(UserRepositoryPort):
    def __init__(self) -> None:
        self._by_id: Dict[str, User] = {}
        self._by_email: Dict[str, User] = {}

    def get_by_id(self, user_id: UserId) -> User | None:
        return self._by_id.get(user_id.value)

    def get_by_email(self, email: EmailAddress) -> User | None:
        return self._by_email.get(email.value)

    def save(self, user: User) -> User:
        self._by_id[user.id.value] = user
        self._by_email[user.email.value] = user
        return user


class SimplePasswordHasher(PasswordHasherPort):
    """
    テスト用の適当なハッシュ。
    実運用の bcrypt とは関係なく、動作だけをテストする。
    """

    def hash(self, raw_password: str) -> HashedPassword:
        # めちゃ適当: "hashed:" をつけるだけ
        return HashedPassword(f"hashed:{raw_password}")

    def verify(self, raw_password: str, hashed_password: HashedPassword) -> bool:
        return hashed_password.value == f"hashed:{raw_password}"


@dataclass(frozen=True)
class FixedTokenPair(TokenPair):
    pass


class FakeTokenService(TokenServicePort):
    """
    実際の JWT ではなく、固定フォーマットの文字列を返すだけ。
    """

    def issue_tokens(self, payload: TokenPayload) -> TokenPair:
        now = datetime(2025, 1, 1, tzinfo=timezone.utc)
        access_exp = now + timedelta(minutes=15)
        refresh_exp = now + timedelta(days=7)
        access = f"access:{payload.user_id}:{payload.plan.value}"
        refresh = f"refresh:{payload.user_id}:{payload.plan.value}"
        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            access_expires_at=access_exp,
            refresh_expires_at=refresh_exp,
        )

    def verify_access_token(self, token: str) -> TokenPayload:
        # "access:user_id:plan" の形を想定
        try:
            prefix, user_id, plan_str = token.split(":")
        except ValueError:
            raise ValueError("invalid token format")
        if prefix != "access":
            raise ValueError("not an access token")
        return TokenPayload(user_id=user_id, plan=UserPlan(plan_str))

    def verify_refresh_token(self, token: str) -> TokenPayload:
        prefix, user_id, plan_str = token.split(":")
        if prefix != "refresh":
            raise ValueError("not a refresh token")
        return TokenPayload(user_id=user_id, plan=UserPlan(plan_str))


class FixedClock(ClockPort):
    def __init__(self, now: Optional[datetime] = None) -> None:
        self._now = now or datetime(2025, 1, 1, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._now


# ---------- pytest fixtures ----------

@pytest.fixture
def user_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def password_hasher() -> SimplePasswordHasher:
    return SimplePasswordHasher()


@pytest.fixture
def token_service() -> FakeTokenService:
    return FakeTokenService()


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock()


# ---------- API クライアント ----------


@pytest.fixture(scope="session")
def app():
    # 本番と同じ create_app を利用
    return create_app()


@pytest.fixture(scope="function")
def client(app):
    # 各テストごとにクリーンなクライアントを渡す
    return TestClient(app)
