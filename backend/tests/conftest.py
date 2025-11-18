from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

# 本番 DI（router / dependencies が Depends しているのはこっち）
from app.di.container import (
    get_register_user_use_case,
    get_login_user_use_case,
    get_logout_user_use_case,
    get_delete_account_use_case,
    get_refresh_token_use_case,
    get_get_current_user_use_case,  # ★ 追加
    get_token_service,              # ★ get_current_user_dto 用
)

# UseCase 本体
from app.application.auth.use_cases.account.register_user import RegisterUserUseCase
from app.application.auth.use_cases.session.login_user import LoginUserUseCase
from app.application.auth.use_cases.session.logout_user import LogoutUserUseCase
from app.application.auth.use_cases.account.delete_account import DeleteAccountUseCase
from app.application.auth.use_cases.session.refresh_token import RefreshTokenUseCase
from app.application.auth.use_cases.current_user.get_current_user import GetCurrentUserUseCase  # ★ 追加

# テスト用 Fake 実装
from tests.fakes.auth_repositories import InMemoryUserRepository
from tests.fakes.auth_services import FakePasswordHasher, FakeTokenService, FixedClock


@pytest.fixture(scope="session")
def user_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture(scope="session")
def password_hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


@pytest.fixture(scope="session")
def token_service() -> FakeTokenService:
    return FakeTokenService()


@pytest.fixture(scope="session")
def clock() -> FixedClock:
    return FixedClock()


@pytest.fixture(scope="session")
def app(
    user_repo: InMemoryUserRepository,
    password_hasher: FakePasswordHasher,
    token_service: FakeTokenService,
    clock: FixedClock,
):
    """
    本番と同じ create_app() を使いつつ、
    auth 周りの UseCase / TokenService を Fake 依存で組み立てたものに差し替える。
    """
    app = create_app()

    # --- UseCase オーバーライド ----------------------------------

    app.dependency_overrides[get_register_user_use_case] = lambda: RegisterUserUseCase(
        user_repo=user_repo,
        password_hasher=password_hasher,
        token_service=token_service,
        clock=clock,
    )

    app.dependency_overrides[get_login_user_use_case] = lambda: LoginUserUseCase(
        user_repo=user_repo,
        password_hasher=password_hasher,
        token_service=token_service,
    )

    app.dependency_overrides[get_logout_user_use_case] = lambda: LogoutUserUseCase(
    )

    app.dependency_overrides[get_delete_account_use_case] = lambda: DeleteAccountUseCase(
        user_repo=user_repo,
        clock=clock,
    )

    app.dependency_overrides[get_refresh_token_use_case] = lambda: RefreshTokenUseCase(
        token_service=token_service,
        user_repo=user_repo,
    )

    # ★ /auth/me, /auth/logout, /auth/me[DELETE] が利用する current_user 用
    app.dependency_overrides[get_get_current_user_use_case] = (
        lambda: GetCurrentUserUseCase(user_repo=user_repo)
    )

    # --- Port オーバーライド（get_current_user_dto 用） -----------

    # get_current_user_dto の token_service も Fake にする
    app.dependency_overrides[get_token_service] = lambda: token_service

    return app


@pytest.fixture(autouse=True)
def _reset_fakes(user_repo: InMemoryUserRepository, clock: FixedClock):
    user_repo.clear()
    clock.reset()
    yield


@pytest.fixture(scope="function")
def client(app) -> TestClient:
    return TestClient(app)
