from __future__ import annotations

import pytest

from tests.fakes.auth_repositories import InMemoryUserRepository
from tests.fakes.auth_services import FakePasswordHasher, FakeTokenService, FixedClock
from tests.fakes.profile_repositories import InMemoryProfileRepository
from app.infra.storage.profile_image_storage import InMemoryProfileImageStorage


# ============================================================
# 共通の Fake ポート（Repo / Hasher / TokenService / Clock）
#   → unit / integration 両方で使いたい軽いやつ
# ============================================================

@pytest.fixture(scope="session")
def user_repo() -> InMemoryUserRepository:
    """
    インメモリの UserRepository。
    セッションスコープで使い回しつつ、各テスト前に clear() する。
    """
    return InMemoryUserRepository()


@pytest.fixture(scope="session")
def password_hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


@pytest.fixture(scope="session")
def token_service() -> FakeTokenService:
    return FakeTokenService()


@pytest.fixture(scope="session")
def clock() -> FixedClock:
    return FixedClock()


@pytest.fixture(scope="session")
def profile_repo() -> InMemoryProfileRepository:
    return InMemoryProfileRepository()


@pytest.fixture(scope="session")
def profile_image_storage() -> InMemoryProfileImageStorage:
    return InMemoryProfileImageStorage()


# ============================================================
# Fake の状態リセット（全テスト共通）
# ============================================================

@pytest.fixture(autouse=True)
def _reset_fakes(
    user_repo: InMemoryUserRepository,
    profile_repo: InMemoryProfileRepository,
    clock: FixedClock,
):
    """
    各テストの前後で Fake の状態をリセットして独立性を保つ。
    unit / integration 両方に効かせたいのでルートで autouse。
    """
    user_repo.clear()
    profile_repo.clear()
    clock.reset()
    yield
