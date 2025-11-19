from __future__ import annotations

import pytest
from datetime import timedelta

from app.application.auth.dto.register_dto import RegisterInputDTO
from app.application.auth.use_cases.account.register_user import RegisterUserUseCase
from app.application.auth.ports.clock_port import ClockPort
from app.application.auth.ports.password_hasher_port import PasswordHasherPort
from app.application.auth.ports.token_service_port import TokenServicePort
from app.application.auth.ports.uow_port import AuthUnitOfWorkPort
from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.domain.auth.entities import User
from app.domain.auth.errors import EmailAlreadyUsedError
from app.domain.auth.value_objects import EmailAddress, UserId, UserPlan, TrialInfo


def _make_use_case(
    auth_uow: AuthUnitOfWorkPort,
    password_hasher: PasswordHasherPort,
    token_service: TokenServicePort,
    clock: ClockPort,
) -> RegisterUserUseCase:
    return RegisterUserUseCase(
        uow=auth_uow,
        password_hasher=password_hasher,
        token_service=token_service,
        clock=clock,
    )


def test_register_user_success(
    auth_uow: AuthUnitOfWorkPort,
    user_repo: UserRepositoryPort,
    password_hasher: PasswordHasherPort,
    token_service: TokenServicePort,
    clock: ClockPort,
) -> None:
    use_case = _make_use_case(auth_uow, password_hasher, token_service, clock)

    input_dto = RegisterInputDTO(
        email="test@example.com",
        password="password123",
        name="Hikaru",
    )

    base_now = clock.now()
    output = use_case.execute(input_dto)

    saved = user_repo.get_by_email(EmailAddress("test@example.com"))
    assert saved is not None
    assert saved.email.value == "test@example.com"
    assert saved.name == "Hikaru"
    assert saved.plan == UserPlan.TRIAL
    assert saved.has_profile is False

    expected_trial_end = base_now + timedelta(days=7)
    assert saved.trial_info.trial_ends_at == expected_trial_end
    assert saved.hashed_password.value.startswith("hashed:")

    assert output.user.email == "test@example.com"
    assert output.user.plan == UserPlan.TRIAL
    assert output.user.trial_ends_at == expected_trial_end
    assert output.tokens.access_token.startswith("access:")
    assert output.tokens.refresh_token.startswith("refresh:")
    assert output.tokens.access_token.split(":")[1] == output.user.id


def test_register_user_email_already_used(
    auth_uow: AuthUnitOfWorkPort,
    user_repo: UserRepositoryPort,
    password_hasher: PasswordHasherPort,
    token_service: TokenServicePort,
    clock: ClockPort,
) -> None:
    existing_user = User(
        id=UserId("user-1"),
        email=EmailAddress("dup@example.com"),
        hashed_password=password_hasher.hash("password123"),
        name="Existing",
        plan=UserPlan.FREE,
        trial_info=TrialInfo(trial_ends_at=None),
        has_profile=False,
        created_at=clock.now(),
    )
    user_repo.save(existing_user)

    use_case = _make_use_case(auth_uow, password_hasher, token_service, clock)

    input_dto = RegisterInputDTO(
        email="dup@example.com",
        password="newpass",
        name="NewUser",
    )

    with pytest.raises(EmailAlreadyUsedError):
        use_case.execute(input_dto)
