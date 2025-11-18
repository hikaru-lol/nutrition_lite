from __future__ import annotations

import pytest

from app.application.auth.use_cases.session.refresh_token import (
    RefreshTokenUseCase,
    RefreshInputDTO,
    InvalidRefreshTokenError,
)
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.domain.auth.entities import User
from app.domain.auth.value_objects import (
    UserId,
    EmailAddress,
    HashedPassword,
    UserPlan,
    TrialInfo,
)


def _create_user(user_id: str, email: str, plan: UserPlan, clock) -> User:
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


def test_refresh_token_success(user_repo, token_service, clock):
    # 1. 事前にユーザーを登録
    user = _create_user("uid-1", "refresh@example.com", UserPlan.TRIAL, clock)
    user_repo.save(user)

    # 2. そのユーザー用の refresh token を発行
    payload = token_service.verify_access_token(
        token_service.issue_tokens(
            payload=type("payload", (), {
                         "user_id": user.id.value, "plan": user.plan})
        ).access_token
    )
    # 上記はちょっとトリッキーなので、単純に issue_tokens から refresh_token を使う
    tokens = token_service.issue_tokens(
        type("payload", (), {"user_id": user.id.value, "plan": user.plan})
    )

    use_case = RefreshTokenUseCase(
        user_repo=user_repo,
        token_service=token_service,
    )

    input_dto = RefreshInputDTO(refresh_token=tokens.refresh_token)
    output = use_case.execute(input_dto)

    assert isinstance(output.user, AuthUserDTO)
    assert output.user.id == user.id.value
    assert output.user.email == user.email.value
    # 新しいトークンが発行されている
    assert output.tokens.access_token.startswith("access:")
    assert output.tokens.refresh_token.startswith("refresh:")


def test_refresh_token_invalid_token(user_repo, token_service):
    use_case = RefreshTokenUseCase(
        user_repo=user_repo,
        token_service=token_service,
    )

    # FakeTokenService は "refresh:user:plan" の形式を期待しているので、
    # 全く違う文字列を渡すと例外になる
    input_dto = RefreshInputDTO(refresh_token="invalid-token-format")

    with pytest.raises(InvalidRefreshTokenError):
        use_case.execute(input_dto)


def test_refresh_token_user_not_found(user_repo, token_service):
    # 存在しないユーザーIDに対するトークンを発行
    tokens = token_service.issue_tokens(
        type("payload", (), {
             "user_id": "non-existent", "plan": UserPlan.TRIAL})
    )

    use_case = RefreshTokenUseCase(
        user_repo=user_repo,
        token_service=token_service,
    )

    input_dto = RefreshInputDTO(refresh_token=tokens.refresh_token)

    from app.application.auth.use_cases.current_user.get_current_user import UserNotFoundError

    with pytest.raises(UserNotFoundError):
        use_case.execute(input_dto)
