from __future__ import annotations

import pytest

from app.application.auth.dto.login_dto import LoginInputDTO
from app.application.auth.use_cases.session.login_user import (
    LoginUserUseCase,
    InvalidCredentialsError,
)
from app.domain.auth.entities import User
from app.domain.auth.value_objects import (
    EmailAddress,
    UserId,
    HashedPassword,
    UserPlan,
    TrialInfo,
)

from app.application.auth.ports.password_hasher_port import PasswordHasherPort
from app.application.auth.ports.clock_port import ClockPort


from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.application.auth.ports.token_service_port import TokenServicePort


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


def test_login_success(user_repo: UserRepositoryPort, password_hasher: PasswordHasherPort, token_service: TokenServicePort, clock: ClockPort):
    user = _create_user("login@example.com", "password123",
                        password_hasher, clock)
    user_repo.save(user)

    use_case = LoginUserUseCase(
        user_repo=user_repo,
        password_hasher=password_hasher,
        token_service=token_service,
    )

    input_dto = LoginInputDTO(
        email="login@example.com", password="password123")
    output = use_case.execute(input_dto)

    assert output.user.email == "login@example.com"
    assert output.tokens.access_token.startswith("access:")
    assert output.tokens.refresh_token.startswith("refresh:")


def test_login_invalid_email(user_repo: UserRepositoryPort, password_hasher: PasswordHasherPort, token_service: TokenServicePort, clock: ClockPort):
    # ユーザーは登録されていない
    use_case = LoginUserUseCase(
        user_repo=user_repo,
        password_hasher=password_hasher,
        token_service=token_service,
    )

    input_dto = LoginInputDTO(
        email="unknown@example.com", password="password123")

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(input_dto)


def test_login_invalid_password(user_repo: UserRepositoryPort, password_hasher: PasswordHasherPort, token_service: TokenServicePort, clock: ClockPort):
    user = _create_user("login2@example.com",
                        "correct-password", password_hasher, clock)
    user_repo.save(user)

    use_case = LoginUserUseCase(
        user_repo=user_repo,
        password_hasher=password_hasher,
        token_service=token_service,
    )

    input_dto = LoginInputDTO(
        email="login2@example.com", password="wrong-password")

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(input_dto)
