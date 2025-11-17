from __future__ import annotations

from datetime import timedelta, timezone, datetime

from app.application.auth.dto.register_dto import RegisterInputDTO
from app.application.auth.use_cases.account.register_user import (
    RegisterUserUseCase,
    EmailAlreadyUsedError,
)
from app.domain.auth.value_objects import UserPlan, EmailAddress, UserId, TrialInfo
from app.domain.auth.entities import User


from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.application.auth.ports.password_hasher_port import PasswordHasherPort
from app.application.auth.ports.token_service_port import TokenServicePort
from app.application.auth.ports.clock_port import ClockPort


def test_register_user_success(user_repo: UserRepositoryPort, password_hasher: PasswordHasherPort, token_service: TokenServicePort, clock: ClockPort):
    use_case = RegisterUserUseCase(
        user_repo=user_repo,
        password_hasher=password_hasher,
        token_service=token_service,
        clock=clock,
    )

    input_dto = RegisterInputDTO(
        email="test@example.com",
        password="password123",
        name="Hikaru",
    )

    output = use_case.execute(input_dto)

    # user_repo に保存されているか
    saved = user_repo.get_by_email(EmailAddress("test@example.com"))
    assert saved is not None
    assert saved.email.value == "test@example.com"
    assert saved.name == "Hikaru"
    assert saved.plan == UserPlan.TRIAL
    assert saved.has_profile is False

    # Trial の終了日時が「固定 now + 7日」になっているか
    expected_trial_end = clock.now() + timedelta(days=7)
    assert saved.trial_info.trial_ends_at == expected_trial_end

    # パスワードがハッシュされているか（SimplePasswordHasher の仕様に従う）
    assert saved.hashed_password.value.startswith("hashed:")

    # 戻り値の DTO も同じ情報を持っているか
    assert output.user.email == "test@example.com"
    assert output.user.plan == UserPlan.TRIAL
    assert output.user.trial_ends_at == expected_trial_end

    # トークンが fake token service の仕様通りか
    assert output.tokens.access_token.startswith("access:")
    assert output.tokens.refresh_token.startswith("refresh:")
    assert output.tokens.access_token.split(":")[1] == output.user.id


def test_register_user_email_already_used(user_repo: UserRepositoryPort, password_hasher: PasswordHasherPort, token_service: TokenServicePort, clock: ClockPort):
    # 事前に同じメールのユーザーを 1 人入れておく
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

    use_case = RegisterUserUseCase(
        user_repo=user_repo,
        password_hasher=password_hasher,
        token_service=token_service,
        clock=clock,
    )

    input_dto = RegisterInputDTO(
        email="dup@example.com",
        password="newpass",
        name="NewUser",
    )

    # 例外が投げられることを確認
    import pytest

    with pytest.raises(EmailAlreadyUsedError):
        use_case.execute(input_dto)
