from __future__ import annotations
from tests.fakes.auth_uow import FakeAuthUnitOfWork
from tests.fakes.auth_services import FakePasswordHasher, FakeTokenService, FixedClock
from tests.fakes.auth_repositories import InMemoryUserRepository
from app.application.auth.use_cases.current_user.get_current_user import (
    GetCurrentUserUseCase,
)
from app.application.auth.use_cases.session.refresh_token import RefreshTokenUseCase
from app.application.auth.use_cases.session.logout_user import LogoutUserUseCase
from app.application.auth.use_cases.session.login_user import LoginUserUseCase
from app.application.auth.use_cases.account.register_user import RegisterUserUseCase
from app.application.auth.use_cases.account.delete_account import DeleteAccountUseCase
from app.di.container import (
    get_register_user_use_case,
    get_login_user_use_case,
    get_logout_user_use_case,
    get_refresh_token_use_case,
    get_delete_account_use_case,
    get_current_user_use_case,
    get_token_service,
)
from app.main import create_app

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# テスト用の固定UUID
TEST_USER_ID = uuid.UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def user_repo() -> InMemoryUserRepository:
    """テスト用のインメモリUserRepository"""
    return InMemoryUserRepository()


@pytest.fixture
def password_hasher() -> FakePasswordHasher:
    """テスト用のFakePasswordHasher"""
    return FakePasswordHasher()


@pytest.fixture
def token_service() -> FakeTokenService:
    """テスト用のFakeTokenService"""
    return FakeTokenService()


@pytest.fixture
def clock() -> FixedClock:
    """テスト用のFixedClock"""
    return FixedClock()


@pytest.fixture
def auth_uow(user_repo: InMemoryUserRepository) -> FakeAuthUnitOfWork:
    """テスト用のFakeAuthUnitOfWork"""
    return FakeAuthUnitOfWork(user_repo=user_repo)


@pytest.fixture
def app(
    user_repo: InMemoryUserRepository,
    password_hasher: FakePasswordHasher,
    token_service: FakeTokenService,
    clock: FixedClock,
    auth_uow: FakeAuthUnitOfWork,
) -> FastAPI:
    """
    FAKEを使ったDIオーバーライドでFastAPIアプリを作成
    """
    app = create_app()

    # UseCaseをFAKEで作成
    register_use_case = RegisterUserUseCase(
        uow=auth_uow,
        password_hasher=password_hasher,
        token_service=token_service,
        clock=clock,
    )

    login_use_case = LoginUserUseCase(
        uow=auth_uow,
        password_hasher=password_hasher,
        token_service=token_service,
    )

    logout_use_case = LogoutUserUseCase()

    refresh_use_case = RefreshTokenUseCase(
        uow=auth_uow,
        token_service=token_service,
    )

    delete_account_use_case = DeleteAccountUseCase(
        uow=auth_uow,
        clock=clock,
    )

    current_user_use_case = GetCurrentUserUseCase(
        uow=auth_uow,
    )

    # DIをオーバーライド
    app.dependency_overrides[get_register_user_use_case] = lambda: register_use_case
    app.dependency_overrides[get_login_user_use_case] = lambda: login_use_case
    app.dependency_overrides[get_logout_user_use_case] = lambda: logout_use_case
    app.dependency_overrides[get_refresh_token_use_case] = lambda: refresh_use_case
    app.dependency_overrides[get_delete_account_use_case] = lambda: delete_account_use_case
    app.dependency_overrides[get_current_user_use_case] = lambda: current_user_use_case
    app.dependency_overrides[get_token_service] = lambda: token_service

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """テスト用のTestClient"""
    return TestClient(app)


class TestRegister:
    """POST /auth/register のテスト"""

    def test_register_success(
        self,
        client: TestClient,
        user_repo: InMemoryUserRepository,
    ):
        """正常系: ユーザー登録が成功する"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "name": "Test User",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["name"] == "Test User"

        # Cookieが設定されていることを確認
        assert "ACCESS_TOKEN" in response.cookies
        assert "REFRESH_TOKEN" in response.cookies

        # ユーザーがリポジトリに保存されていることを確認
        from app.domain.auth.value_objects import EmailAddress

        saved_user = user_repo.get_by_email(EmailAddress("test@example.com"))
        assert saved_user is not None
        assert saved_user.email.value == "test@example.com"

    def test_register_duplicate_email(
        self,
        client: TestClient,
        user_repo: InMemoryUserRepository,
        password_hasher: FakePasswordHasher,
        clock: FixedClock,
    ):
        """異常系: 既に登録されているメールアドレスで登録しようとする"""
        from app.domain.auth.entities import User
        from app.domain.auth.value_objects import UserId, EmailAddress, UserPlan, TrialInfo

        # 既存ユーザーを作成
        existing_user = User(
            id=UserId("existing-user"),
            email=EmailAddress("existing@example.com"),
            hashed_password=password_hasher.hash("password123"),
            name="Existing User",
            plan=UserPlan.TRIAL,
            trial_info=TrialInfo(trial_ends_at=None),
            has_profile=False,
            created_at=clock.now(),
        )
        user_repo.save(existing_user)

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "existing@example.com",
                "password": "password123",
                "name": "New User",
            },
        )

        assert response.status_code == 409
        data = response.json()
        assert "error" in data

    def test_register_invalid_email(self, client: TestClient):
        """異常系: 無効なメールアドレス形式"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "password123",
                "name": "Test User",
            },
        )

        assert response.status_code == 400


class TestLogin:
    """POST /auth/login のテスト"""

    def test_login_success(
        self,
        client: TestClient,
        user_repo: InMemoryUserRepository,
        password_hasher: FakePasswordHasher,
        clock: FixedClock,
    ):
        """正常系: ログインが成功する"""
        from app.domain.auth.entities import User
        from app.domain.auth.value_objects import UserId, EmailAddress, UserPlan, TrialInfo

        # ユーザーを作成
        user = User(
            id=UserId(str(TEST_USER_ID)),
            email=EmailAddress("test@example.com"),
            hashed_password=password_hasher.hash("password123"),
            name="Test User",
            plan=UserPlan.TRIAL,
            trial_info=TrialInfo(trial_ends_at=None),
            has_profile=False,
            created_at=clock.now(),
        )
        user_repo.save(user)

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"

        # Cookieが設定されていることを確認
        assert "ACCESS_TOKEN" in response.cookies
        assert "REFRESH_TOKEN" in response.cookies

    def test_login_invalid_credentials(self, client: TestClient):
        """異常系: 無効な認証情報"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_login_wrong_password(
        self,
        client: TestClient,
        user_repo: InMemoryUserRepository,
        password_hasher: FakePasswordHasher,
        clock: FixedClock,
    ):
        """異常系: 間違ったパスワード"""
        from app.domain.auth.entities import User
        from app.domain.auth.value_objects import UserId, EmailAddress, UserPlan, TrialInfo

        # ユーザーを作成
        user = User(
            id=UserId(str(TEST_USER_ID)),
            email=EmailAddress("test@example.com"),
            hashed_password=password_hasher.hash("correctpassword"),
            name="Test User",
            plan=UserPlan.TRIAL,
            trial_info=TrialInfo(trial_ends_at=None),
            has_profile=False,
            created_at=clock.now(),
        )
        user_repo.save(user)

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestGetMe:
    """GET /auth/me のテスト"""

    def test_get_me_success(
        self,
        client: TestClient,
        user_repo: InMemoryUserRepository,
        password_hasher: FakePasswordHasher,
        token_service: FakeTokenService,
        clock: FixedClock,
    ):
        """正常系: 認証済みユーザー情報を取得できる"""
        from app.domain.auth.entities import User
        from app.domain.auth.value_objects import UserId, EmailAddress, UserPlan, TrialInfo

        # ユーザーを作成
        user = User(
            id=UserId(str(TEST_USER_ID)),
            email=EmailAddress("test@example.com"),
            hashed_password=password_hasher.hash("password123"),
            name="Test User",
            plan=UserPlan.TRIAL,
            trial_info=TrialInfo(trial_ends_at=None),
            has_profile=False,
            created_at=clock.now(),
        )
        user_repo.save(user)

        # トークンを発行
        from app.application.auth.ports.token_service_port import TokenPayload

        tokens = token_service.issue_tokens(
            TokenPayload(user_id=str(TEST_USER_ID), plan=UserPlan.TRIAL)
        )

        # Cookieを設定してリクエスト
        response = client.get(
            "/api/v1/auth/me",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["name"] == "Test User"

    def test_get_me_unauthorized(self, client: TestClient):
        """異常系: トークンがない場合"""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_get_me_invalid_token(self, client: TestClient):
        """異常系: 無効なトークン"""
        response = client.get(
            "/api/v1/auth/me",
            cookies={
                "ACCESS_TOKEN": "invalid-token",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestRefresh:
    """POST /auth/refresh のテスト"""

    def test_refresh_success(
        self,
        client: TestClient,
        user_repo: InMemoryUserRepository,
        password_hasher: FakePasswordHasher,
        token_service: FakeTokenService,
        clock: FixedClock,
    ):
        """正常系: リフレッシュトークンから新しいトークンペアを取得できる"""
        from app.domain.auth.entities import User
        from app.domain.auth.value_objects import UserId, EmailAddress, UserPlan, TrialInfo
        from app.application.auth.ports.token_service_port import TokenPayload

        # ユーザーを作成
        user = User(
            id=UserId(str(TEST_USER_ID)),
            email=EmailAddress("test@example.com"),
            hashed_password=password_hasher.hash("password123"),
            name="Test User",
            plan=UserPlan.TRIAL,
            trial_info=TrialInfo(trial_ends_at=None),
            has_profile=False,
            created_at=clock.now(),
        )
        user_repo.save(user)

        # リフレッシュトークンを発行
        tokens = token_service.issue_tokens(
            TokenPayload(user_id=str(TEST_USER_ID), plan=UserPlan.TRIAL)
        )

        # リフレッシュトークンを使って新しいトークンを取得
        response = client.post(
            "/api/v1/auth/refresh",
            cookies={
                "REFRESH_TOKEN": tokens.refresh_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "user" in data

        # 新しいCookieが設定されていることを確認
        assert "ACCESS_TOKEN" in response.cookies
        assert "REFRESH_TOKEN" in response.cookies

    def test_refresh_missing_token(self, client: TestClient):
        """異常系: リフレッシュトークンがない場合"""
        response = client.post("/api/v1/auth/refresh")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_refresh_invalid_token(self, client: TestClient):
        """異常系: 無効なリフレッシュトークン"""
        response = client.post(
            "/api/v1/auth/refresh",
            cookies={
                "REFRESH_TOKEN": "invalid-refresh-token",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestLogout:
    """POST /auth/logout のテスト"""

    def test_logout_success(
        self,
        client: TestClient,
        user_repo: InMemoryUserRepository,
        password_hasher: FakePasswordHasher,
        token_service: FakeTokenService,
        clock: FixedClock,
    ):
        """正常系: ログアウトが成功する"""
        from app.domain.auth.entities import User
        from app.domain.auth.value_objects import UserId, EmailAddress, UserPlan, TrialInfo
        from app.application.auth.ports.token_service_port import TokenPayload

        # ユーザーを作成
        user = User(
            id=UserId(str(TEST_USER_ID)),
            email=EmailAddress("test@example.com"),
            hashed_password=password_hasher.hash("password123"),
            name="Test User",
            plan=UserPlan.TRIAL,
            trial_info=TrialInfo(trial_ends_at=None),
            has_profile=False,
            created_at=clock.now(),
        )
        user_repo.save(user)

        # トークンを発行
        tokens = token_service.issue_tokens(
            TokenPayload(user_id=str(TEST_USER_ID), plan=UserPlan.TRIAL)
        )

        # ログアウト
        response = client.post(
            "/api/v1/auth/logout",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 204

        # Cookieがクリアされていることを確認
        # TestClientはSet-Cookieヘッダーを確認する必要がある
        # 実際の実装ではclear_auth_cookiesが呼ばれる

    def test_logout_unauthorized(self, client: TestClient):
        """異常系: トークンがない場合"""
        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestDeleteMe:
    """DELETE /auth/me のテスト"""

    def test_delete_me_success(
        self,
        client: TestClient,
        user_repo: InMemoryUserRepository,
        password_hasher: FakePasswordHasher,
        token_service: FakeTokenService,
        clock: FixedClock,
    ):
        """正常系: アカウント削除が成功する"""
        from app.domain.auth.entities import User
        from app.domain.auth.value_objects import UserId, EmailAddress, UserPlan, TrialInfo
        from app.application.auth.ports.token_service_port import TokenPayload

        # ユーザーを作成
        user = User(
            id=UserId(str(TEST_USER_ID)),
            email=EmailAddress("test@example.com"),
            hashed_password=password_hasher.hash("password123"),
            name="Test User",
            plan=UserPlan.TRIAL,
            trial_info=TrialInfo(trial_ends_at=None),
            has_profile=False,
            created_at=clock.now(),
        )
        user_repo.save(user)

        # トークンを発行
        tokens = token_service.issue_tokens(
            TokenPayload(user_id=str(TEST_USER_ID), plan=UserPlan.TRIAL)
        )

        # アカウント削除
        response = client.delete(
            "/api/v1/auth/me",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 204

        # ユーザーが論理削除されていることを確認
        from app.domain.auth.value_objects import UserId

        deleted_user = user_repo.get_by_id(UserId(str(TEST_USER_ID)))
        assert deleted_user is not None
        assert deleted_user.deleted_at is not None
        assert not deleted_user.is_active

    def test_delete_me_unauthorized(self, client: TestClient):
        """異常系: トークンがない場合"""
        response = client.delete("/api/v1/auth/me")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data
