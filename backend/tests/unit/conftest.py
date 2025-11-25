from __future__ import annotations

import pytest

from tests.fakes.auth_repositories import InMemoryUserRepository
from tests.fakes.auth_uow import FakeAuthUnitOfWork


@pytest.fixture
def auth_uow(user_repo: InMemoryUserRepository) -> FakeAuthUnitOfWork:
    """
    ユニットテスト用の Fake UoW。
    RegisterUserUseCase などを直接テストするときに利用。
    """
    return FakeAuthUnitOfWork(user_repo=user_repo)
