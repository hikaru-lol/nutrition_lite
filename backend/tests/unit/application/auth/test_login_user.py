from __future__ import annotations

import pytest

from app.application.auth.dto.login_dto import LoginInputDTO
from app.application.auth.use_cases.session.login_user import LoginUserUseCase
from app.application.auth.ports.clock_port import ClockPort
from app.application.auth.ports.password_hasher_port import PasswordHasherPort
from app.application.auth.ports.token_service_port import TokenServicePort
from app.application.auth.ports.uow_port import AuthUnitOfWorkPort
from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.domain.auth.entities import User
from app.domain.auth.errors import InvalidCredentialsError
from app.domain.auth.value_objects import (
    EmailAddress,
    UserId,
    UserPlan,
    TrialInfo,
)


def _create_user(email: str, password: str, password_hasher: PasswordHasherPort, clock: ClockPort) -> User:
    return User(
        id=UserId("user-1"),
        email=EmailAddress(email),
        hashed_password=password_hasher.hash(password),
        name="Hikaru",
        plan=UserPlan.TRIAL,
        trial_info=TrialInfo(trial_ends_at=clock.now()),
        has_profile=False,
        created_at=clock.now(),
    )


def _make_use_case(
    auth_uow: AuthUnitOfWorkPort,
    password_hasher: PasswordHasherPort,
    token_service: TokenServicePort,
) -> LoginUserUseCase:
    return LoginUserUseCase(
        uow=auth_uow,
        password_hasher=password_hasher,
        token_service=token_service,
    )


def test_login_success(
    auth_uow: AuthUnitOfWorkPort,
    user_repo: UserRepositoryPort,
    password_hasher: PasswordHasherPort,
    token_service: TokenServicePort,
    clock: ClockPort,
) -> None:
    user = _create_user("login@example.com", "password123", password_hasher, clock)
    user_repo.save(user)

    use_case = _make_use_case(auth_uow, password_hasher, token_service)

    input_dto = LoginInputDTO(email="login@example.com", password="password123")
    output = use_case.execute(input_dto)

    assert output.user.email == "login@example.com"
    assert output.tokens.access_token.startswith("access:")
    assert output.tokens.refresh_token.startswith("refresh:")


def test_login_invalid_email(
    auth_uow: AuthUnitOfWorkPort,
    password_hasher: PasswordHasherPort,
    token_service: TokenServicePort,
) -> None:
    use_case = _make_use_case(auth_uow, password_hasher, token_service)
    input_dto = LoginInputDTO(email="unknown@example.com", password="password123")

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(input_dto)


def test_login_invalid_password(
    auth_uow: AuthUnitOfWorkPort,
    user_repo: UserRepositoryPort,
    password_hasher: PasswordHasherPort,
    token_service: TokenServicePort,
    clock: ClockPort,
) -> None:
    user = _create_user("login2@example.com", "correct-password", password_hasher, clock)
    user_repo.save(user)

    use_case = _make_use_case(auth_uow, password_hasher, token_service)

    input_dto = LoginInputDTO(email="login2@example.com", password="wrong-password")

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(input_dto)
