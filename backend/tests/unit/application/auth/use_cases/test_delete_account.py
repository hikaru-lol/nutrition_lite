from __future__ import annotations

import pytest

from app.application.auth.use_cases.account.delete_account import DeleteAccountUseCase
from app.application.auth.use_cases.current_user.get_current_user import UserNotFoundError
from app.domain.auth.entities import User
from app.domain.auth.value_objects import (
    UserId,
    EmailAddress,
    HashedPassword,
    UserPlan,
    TrialInfo,
)


def _create_user(user_id: str, email: str, clock) -> User:
    return User(
        id=UserId(user_id),
        email=EmailAddress(email),
        hashed_password=HashedPassword("hashed:dummy"),
        name="Hikaru",
        plan=UserPlan.FREE,
        trial_info=TrialInfo(trial_ends_at=None),
        has_profile=True,
        created_at=clock.now(),
    )


def test_delete_account_success(user_repo, clock):
    user = _create_user("uid-del-1", "delete@example.com", clock)
    user_repo.save(user)

    use_case = DeleteAccountUseCase(
        user_repo=user_repo,
        clock=clock,
    )

    use_case.execute(user_id="uid-del-1")

    deleted = user_repo.get_by_id(UserId("uid-del-1"))
    assert deleted is not None
    assert deleted.deleted_at is not None
    assert deleted.is_active is False


def test_delete_account_user_not_found(user_repo, clock):
    use_case = DeleteAccountUseCase(
        user_repo=user_repo,
        clock=clock,
    )

    with pytest.raises(UserNotFoundError):
        use_case.execute(user_id="unknown-id")
