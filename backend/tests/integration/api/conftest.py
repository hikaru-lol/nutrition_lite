from __future__ import annotations

import os
import pytest
from fastapi.testclient import TestClient

from app.main import create_app

from app.di.container import (
    get_register_user_use_case,
    get_login_user_use_case,
    get_logout_user_use_case,
    get_delete_account_use_case,
    get_refresh_token_use_case,
    get_current_user_use_case,
    get_token_service,
    get_upsert_profile_use_case,
    get_get_my_profile_use_case,
)

from app.application.auth.use_cases.account.register_user import RegisterUserUseCase
from app.application.auth.use_cases.session.login_user import LoginUserUseCase
from app.application.auth.use_cases.session.logout_user import LogoutUserUseCase
from app.application.auth.use_cases.account.delete_account import DeleteAccountUseCase
from app.application.auth.use_cases.session.refresh_token import RefreshTokenUseCase
from app.application.auth.use_cases.current_user.get_current_user import (
    GetCurrentUserUseCase,
)

from app.application.profile.use_cases.upsert_profile import UpsertProfileUseCase
from app.application.profile.use_cases.get_my_profile import GetMyProfileUseCase

from tests.fakes.auth_repositories import InMemoryUserRepository
from tests.fakes.auth_services import FakePasswordHasher, FakeTokenService, FixedClock
from tests.fakes.auth_uow import FakeAuthUnitOfWork
from tests.fakes.profile_repositories import InMemoryProfileRepository
from tests.fakes.profile_uow import FakeProfileUnitOfWork
from app.infra.storage.profile_image_storage import InMemoryProfileImageStorage


USE_FAKE_INFRA = os.getenv("USE_FAKE_INFRA", "true").lower() in (
    "1",
    "true",
    "yes",
    "on",
)


# ============================================================
# FastAPI アプリ & dependency_overrides（API 統合テスト用）
# ============================================================

@pytest.fixture(scope="session")
def app(
    user_repo: InMemoryUserRepository,
    password_hasher: FakePasswordHasher,
    token_service: FakeTokenService,
    clock: FixedClock,
    profile_repo: InMemoryProfileRepository,
    profile_image_storage: InMemoryProfileImageStorage,
):
    """
    本番と同じ create_app() を使いつつ、
    auth/profile 周りを Fake に差し替えた FastAPI アプリ。
    ※ この fixture は integration テストでのみ読み込まれる。
    """
    app = create_app()

    if USE_FAKE_INFRA:

        def make_auth_uow() -> FakeAuthUnitOfWork:
            return FakeAuthUnitOfWork(user_repo=user_repo)

        app.dependency_overrides[get_register_user_use_case] = (
            lambda: RegisterUserUseCase(
                uow=make_auth_uow(),
                password_hasher=password_hasher,
                token_service=token_service,
                clock=clock,
            )
        )

        app.dependency_overrides[get_login_user_use_case] = (
            lambda: LoginUserUseCase(
                uow=make_auth_uow(),
                password_hasher=password_hasher,
                token_service=token_service,
            )
        )

        app.dependency_overrides[get_logout_user_use_case] = (
            lambda: LogoutUserUseCase()
        )

        app.dependency_overrides[get_delete_account_use_case] = (
            lambda: DeleteAccountUseCase(
                uow=make_auth_uow(),
                clock=clock,
            )
        )

        app.dependency_overrides[get_refresh_token_use_case] = (
            lambda: RefreshTokenUseCase(
                uow=make_auth_uow(),
                token_service=token_service,
            )
        )

        app.dependency_overrides[get_current_user_use_case] = (
            lambda: GetCurrentUserUseCase(uow=make_auth_uow())
        )

        def make_profile_uow() -> FakeProfileUnitOfWork:
            return FakeProfileUnitOfWork(profile_repo=profile_repo)

        app.dependency_overrides[get_upsert_profile_use_case] = (
            lambda: UpsertProfileUseCase(
                uow=make_profile_uow(),
                image_storage=profile_image_storage,
            )
        )

        app.dependency_overrides[get_get_my_profile_use_case] = (
            lambda: GetMyProfileUseCase(
                uow=make_profile_uow(),
            )
        )

        app.dependency_overrides[get_token_service] = lambda: token_service

    # USE_FAKE_INFRA=false の場合は dependency_overrides せず
    return app


# ============================================================
# TestClient フィクスチャ（API 統合テスト用）
# ============================================================

@pytest.fixture(scope="function")
def client(app) -> TestClient:
    """
    FastAPI TestClient。
    /api/v1/** を実際の HTTP と同じように叩くために利用。
    """
    return TestClient(app)
