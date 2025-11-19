from __future__ import annotations

import pytest

from app.application.auth.dto.refresh_dto import RefreshInputDTO
from app.application.auth.ports.clock_port import ClockPort
from app.application.auth.ports.token_service_port import (
    TokenPayload,
    TokenServicePort,
)
from app.application.auth.ports.uow_port import AuthUnitOfWorkPort
from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.application.auth.use_cases.session.refresh_token import RefreshTokenUseCase
from app.domain.auth.entities import User
from app.domain.auth.errors import InvalidRefreshTokenError, UserNotFoundError
from app.domain.auth.value_objects import (
    EmailAddress,
    HashedPassword,
    TrialInfo,
    UserId,
    UserPlan,
)


def _create_user(user_id: str, email: str, plan: UserPlan, clock: ClockPort) -> User:
    return User(
        id=UserId(user_id),
        email=EmailAddress(email),
        hashed_password=HashedPassword("hashed:dummy"),
        name="Hikaru",
        plan=plan,
        trial_info=TrialInfo(trial_ends_at=None),
        has_profile=False,
        created_at=clock.now(),
    )


def _make_use_case(
    auth_uow: AuthUnitOfWorkPort,
    token_service: TokenServicePort,
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(
        uow=auth_uow,
        token_service=token_service,
    )


def test_refresh_token_success(
    auth_uow: AuthUnitOfWorkPort,
    user_repo: UserRepositoryPort,
    token_service: TokenServicePort,
    clock: ClockPort,
) -> None:
    user = _create_user("uid-1", "refresh@example.com", UserPlan.TRIAL, clock)
    user_repo.save(user)

    tokens = token_service.issue_tokens(
        TokenPayload(user_id=user.id.value, plan=user.plan)
    )

    use_case = _make_use_case(auth_uow, token_service)

    input_dto = RefreshInputDTO(refresh_token=tokens.refresh_token)
    output = use_case.execute(input_dto)

    assert output.user.id == user.id.value
    assert output.user.email == user.email.value
    assert output.tokens.access_token.startswith("access:")
    assert output.tokens.refresh_token.startswith("refresh:")


def test_refresh_token_invalid_token(
    auth_uow: AuthUnitOfWorkPort,
    token_service: TokenServicePort,
) -> None:
    use_case = _make_use_case(auth_uow, token_service)
    input_dto = RefreshInputDTO(refresh_token="invalid-token-format")

    with pytest.raises(InvalidRefreshTokenError):
        use_case.execute(input_dto)


def test_refresh_token_user_not_found(
    auth_uow: AuthUnitOfWorkPort,
    token_service: TokenServicePort,
) -> None:
    tokens = token_service.issue_tokens(
        TokenPayload(user_id="non-existent", plan=UserPlan.TRIAL)
    )

    use_case = _make_use_case(auth_uow, token_service)
    input_dto = RefreshInputDTO(refresh_token=tokens.refresh_token)

    with pytest.raises(UserNotFoundError):
        use_case.execute(input_dto)
