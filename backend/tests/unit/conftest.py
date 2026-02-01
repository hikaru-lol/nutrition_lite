from __future__ import annotations

import pytest

from tests.fakes.auth_repositories import InMemoryUserRepository
from tests.fakes.auth_uow import FakeAuthUnitOfWork
from tests.fakes.calendar_repositories import InMemoryCalendarRepository
from tests.fakes.calendar_uow import FakeCalendarUnitOfWork


@pytest.fixture
def auth_uow(user_repo: InMemoryUserRepository) -> FakeAuthUnitOfWork:
    """
    ユニットテスト用の Fake UoW。
    RegisterUserUseCase などを直接テストするときに利用。
    """
    return FakeAuthUnitOfWork(user_repo=user_repo)


@pytest.fixture
def calendar_uow(calendar_repo: InMemoryCalendarRepository) -> FakeCalendarUnitOfWork:
    """
    ユニットテスト用のカレンダー Fake UoW。
    GetMonthlyCalendarUseCase などを直接テストするときに利用。
    """
    return FakeCalendarUnitOfWork(calendar_repo=calendar_repo)
