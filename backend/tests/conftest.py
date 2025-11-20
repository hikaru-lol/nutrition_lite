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
    get_get_current_user_use_case,
    get_token_service,
)

# UseCase 本体（auth 用）
from app.application.auth.use_cases.account.register_user import RegisterUserUseCase
from app.application.auth.use_cases.session.login_user import LoginUserUseCase
from app.application.auth.use_cases.session.logout_user import LogoutUserUseCase
from app.application.auth.use_cases.account.delete_account import DeleteAccountUseCase
from app.application.auth.use_cases.session.refresh_token import RefreshTokenUseCase
from app.application.auth.use_cases.current_user.get_current_user import GetCurrentUserUseCase

# テスト用 Fake 実装
from tests.fakes.auth_repositories import InMemoryUserRepository
from tests.fakes.auth_services import FakePasswordHasher, FakeTokenService, FixedClock
from tests.fakes.auth_uow import FakeAuthUnitOfWork


# ★ 追加：profile 用 UseCase / DI
from app.application.profile.use_cases.upsert_profile import UpsertProfileUseCase
from app.application.profile.use_cases.get_my_profile import GetMyProfileUseCase
from app.di.container import (
    get_upsert_profile_use_case,
    get_get_my_profile_use_case,
)

# profile 用 Fake
from tests.fakes.profile_repositories import InMemoryProfileRepository
from tests.fakes.profile_uow import FakeProfileUnitOfWork
from app.infra.storage.profile_image_storage import InMemoryProfileImageStorage

# ============================================================
# 共通の Fake ポート（Repo / Hasher / TokenService / Clock）
# ============================================================


@pytest.fixture(scope="session")
def user_repo() -> InMemoryUserRepository:
    """
    インメモリの UserRepository。
    セッションスコープで使い回しつつ、各テスト前に clear() する。
    """
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


# ★ 追加：profile 用 Fake ポート
@pytest.fixture(scope="session")
def profile_repo() -> InMemoryProfileRepository:
    return InMemoryProfileRepository()


@pytest.fixture(scope="session")
def profile_image_storage() -> InMemoryProfileImageStorage:
    return InMemoryProfileImageStorage()

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
    auth 周りの UseCase / TokenService / UoW を Fake に差し替えた FastAPI アプリ。
    """
    app = create_app()

    def make_auth_uow() -> FakeAuthUnitOfWork:
        # 各 UseCase 解決時に新しい UoW を生成（Repo は共有）
        return FakeAuthUnitOfWork(user_repo=user_repo)

    # --- UseCase オーバーライド ----------------------------------

    app.dependency_overrides[get_register_user_use_case] = lambda: RegisterUserUseCase(
        uow=make_auth_uow(),
        password_hasher=password_hasher,
        token_service=token_service,
        clock=clock,
    )

    app.dependency_overrides[get_login_user_use_case] = lambda: LoginUserUseCase(
        uow=make_auth_uow(),
        password_hasher=password_hasher,
        token_service=token_service,
    )

    app.dependency_overrides[get_logout_user_use_case] = lambda: LogoutUserUseCase(
    )

    app.dependency_overrides[get_delete_account_use_case] = lambda: DeleteAccountUseCase(
        uow=make_auth_uow(),
        clock=clock,
    )

    app.dependency_overrides[get_refresh_token_use_case] = lambda: RefreshTokenUseCase(
        uow=make_auth_uow(),
        token_service=token_service,
    )

    # /auth/me, /auth/logout, /auth/me[DELETE] で使われる current_user 用 UseCase
    app.dependency_overrides[get_get_current_user_use_case] = (
        lambda: GetCurrentUserUseCase(uow=make_auth_uow())
    )

    # --- Port オーバーライド（get_current_user_dto 内など） ------
    def make_profile_uow() -> FakeProfileUnitOfWork:
        # 各 UseCase 解決時に新しい UoW を作るが、profile_repo は共有
        return FakeProfileUnitOfWork(profile_repo=profile_repo)

    app.dependency_overrides[get_upsert_profile_use_case] = lambda: UpsertProfileUseCase(
        uow=make_profile_uow(),
        image_storage=profile_image_storage,
    )

    app.dependency_overrides[get_get_my_profile_use_case] = lambda: GetMyProfileUseCase(
        uow=make_profile_uow(),
    )

    # get_current_user_dto の token_service も Fake にする
    app.dependency_overrides[get_token_service] = lambda: token_service

    return app


# ============================================================
# Fake の状態リセット（全テスト共通）
# ============================================================


@pytest.fixture(autouse=True)
def _reset_fakes(user_repo: InMemoryUserRepository, profile_repo: InMemoryProfileRepository, clock: FixedClock):
    """
    各テストの前後で Fake の状態をリセットして独立性を保つ。
    """
    user_repo.clear()
    profile_repo.clear()
    clock.reset()
    yield
    # 後処理があればここに（今は特になし）


# ============================================================
# TestClient フィクスチャ（API 統合テスト用）
# ============================================================


@pytest.fixture(scope="function")
def client(app) -> TestClient:
    """
    FastAPI TestClient。
    /api/v1/auth/** を実際の HTTP と同じように叩くために利用。
    """
    return TestClient(app)


# ============================================================
# ユースケース単体テスト用の Fixture（任意で利用）
# ============================================================


@pytest.fixture
def auth_uow(user_repo: InMemoryUserRepository) -> FakeAuthUnitOfWork:
    """
    ユニットテスト用の Fake UoW。
    RegisterUserUseCase などを直接テストするときに利用。
    """
    return FakeAuthUnitOfWork(user_repo=user_repo)


# @pytest.fixture
# def register_use_case(
#     auth_uow: FakeAuthUnitOfWork,
#     password_hasher: FakePasswordHasher,
#     token_service: FakeTokenService,
#     clock: FixedClock,
# ) -> RegisterUserUseCase:
#     """
#     RegisterUserUseCase のユニットテスト用。
#     API 統合テストでは使わず、tests/unit/... から使う想定。
#     """
#     return RegisterUserUseCase(
#         uow=auth_uow,
#         password_hasher=password_hasher,
#         token_service=token_service,
#         clock=clock,
#     )
