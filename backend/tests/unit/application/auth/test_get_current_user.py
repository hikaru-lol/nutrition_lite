from __future__ import annotations

import pytest

from app.application.auth.ports.clock_port import ClockPort
from app.application.auth.ports.uow_port import AuthUnitOfWorkPort
from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.application.auth.use_cases.current_user.get_current_user import GetCurrentUserUseCase
from app.domain.auth.entities import User
from app.domain.auth.errors import UserNotFoundError
from app.domain.auth.value_objects import (
    EmailAddress,
    HashedPassword,
    TrialInfo,
    UserId,
    UserPlan,
)


def test_get_current_user_success(
    auth_uow: AuthUnitOfWorkPort,
    user_repo: UserRepositoryPort,
    clock: ClockPort,
) -> None:
    user = User(
        id=UserId("uid-123"),
        email=EmailAddress("me@example.com"),
        hashed_password=HashedPassword("hashed:dummy"),
        name="Me",
        plan=UserPlan.FREE,
        trial_info=TrialInfo(trial_ends_at=None),
        has_profile=True,
        created_at=clock.now(),
    )
    user_repo.save(user)

    use_case = GetCurrentUserUseCase(uow=auth_uow)

    dto = use_case.execute("uid-123")

    assert dto.id == "uid-123"
    assert dto.email == "me@example.com"
    assert dto.has_profile is True
    assert dto.plan == UserPlan.FREE


def test_get_current_user_not_found(auth_uow: AuthUnitOfWorkPort) -> None:
    use_case = GetCurrentUserUseCase(uow=auth_uow)

    with pytest.raises(UserNotFoundError):
        use_case.execute("unknown-id")
