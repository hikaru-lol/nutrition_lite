from __future__ import annotations

import uuid
from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.domain.auth.entities import User
from app.application.auth.ports.token_service_port import TokenPair
from app.di.container import (
    get_current_user_use_case,
    get_my_profile_use_case,
    get_profile_image_storage,
    get_profile_uow,
    get_token_service,
    get_upsert_profile_use_case,
)
from app.main import create_app
from app.application.auth.use_cases.current_user.get_current_user import (
    GetCurrentUserUseCase,
)
from app.application.profile.use_cases.get_my_profile import GetMyProfileUseCase
from app.application.profile.use_cases.upsert_profile import UpsertProfileUseCase
from tests.fakes.auth_repositories import InMemoryUserRepository
from tests.fakes.auth_services import FakePasswordHasher, FakeTokenService, FixedClock
from tests.fakes.auth_uow import FakeAuthUnitOfWork
from tests.fakes.profile_repositories import InMemoryProfileRepository
from tests.fakes.profile_uow import FakeProfileUnitOfWork
from app.infra.storage.profile_image_storage import InMemoryProfileImageStorage

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
def profile_repo() -> InMemoryProfileRepository:
    """テスト用のインメモリProfileRepository"""
    return InMemoryProfileRepository()


@pytest.fixture
def profile_uow(profile_repo: InMemoryProfileRepository) -> FakeProfileUnitOfWork:
    """テスト用のFakeProfileUnitOfWork"""
    return FakeProfileUnitOfWork(profile_repo=profile_repo)


@pytest.fixture
def profile_image_storage() -> InMemoryProfileImageStorage:
    """テスト用のInMemoryProfileImageStorage"""
    return InMemoryProfileImageStorage()


@pytest.fixture
def app(
    user_repo: InMemoryUserRepository,
    password_hasher: FakePasswordHasher,
    token_service: FakeTokenService,
    clock: FixedClock,
    auth_uow: FakeAuthUnitOfWork,
    profile_uow: FakeProfileUnitOfWork,
    profile_image_storage: InMemoryProfileImageStorage,
) -> FastAPI:
    """
    FAKEを使ったDIオーバーライドでFastAPIアプリを作成
    """
    app = create_app()

    # UseCaseをFAKEで作成
    current_user_use_case = GetCurrentUserUseCase(
        uow=auth_uow,
    )

    my_profile_use_case = GetMyProfileUseCase(
        uow=profile_uow,
    )

    upsert_profile_use_case = UpsertProfileUseCase(
        uow=profile_uow,
        image_storage=profile_image_storage,
    )

    # DIをオーバーライド
    app.dependency_overrides[get_current_user_use_case] = lambda: current_user_use_case
    app.dependency_overrides[get_token_service] = lambda: token_service
    app.dependency_overrides[get_profile_uow] = lambda: profile_uow
    app.dependency_overrides[get_profile_image_storage] = lambda: profile_image_storage
    app.dependency_overrides[get_my_profile_use_case] = lambda: my_profile_use_case
    app.dependency_overrides[get_upsert_profile_use_case] = lambda: upsert_profile_use_case

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """テスト用のTestClient"""
    return TestClient(app)


@pytest.fixture
def authenticated_user(
    user_repo: InMemoryUserRepository,
    password_hasher: FakePasswordHasher,
    token_service: FakeTokenService,
    clock: FixedClock,
):
    """認証済みユーザーとトークンを作成するヘルパー"""
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

    return user, tokens


class TestGetMyProfile:
    """GET /profile/me のテスト"""

    def test_get_my_profile_success(
        self,
        client: TestClient,
        profile_repo: InMemoryProfileRepository,
        authenticated_user: tuple[User, TokenPair],
        clock: FixedClock,
    ):
        """正常系: プロフィールが存在する場合"""
        user, tokens = authenticated_user

        # プロフィールを作成
        from app.domain.profile.entities import Profile
        from app.domain.profile.value_objects import HeightCm, WeightKg
        from app.domain.profile.value_objects import Sex

        profile = Profile(
            user_id=user.id,
            sex=Sex.MALE,
            birthdate=date(1990, 1, 1),
            height_cm=HeightCm(175.0),
            weight_kg=WeightKg(70.0),
            image_id=None,
            meals_per_day=3,
            created_at=clock.now(),
            updated_at=clock.now(),
        )
        profile_repo.save(profile)

        # プロフィールを取得
        response = client.get(
            "/api/v1/profile/me",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(TEST_USER_ID)
        assert data["sex"] == "male"
        assert data["birthdate"] == "1990-01-01"
        assert data["height_cm"] == 175.0
        assert data["weight_kg"] == 70.0
        assert data["meals_per_day"] == 3

    def test_get_my_profile_not_found(
        self,
        client: TestClient,
        authenticated_user,
    ):
        """異常系: プロフィールが存在しない場合"""
        _, tokens = authenticated_user

        response = client.get(
            "/api/v1/profile/me",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_get_my_profile_unauthorized(self, client: TestClient):
        """異常系: トークンがない場合"""
        response = client.get("/api/v1/profile/me")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestUpsertMyProfile:
    """PUT /profile/me のテスト"""

    def test_upsert_my_profile_create(
        self,
        client: TestClient,
        profile_repo: InMemoryProfileRepository,
        authenticated_user,
        clock: FixedClock,
    ):
        """正常系: 新規プロフィール作成"""
        _, tokens = authenticated_user

        response = client.put(
            "/api/v1/profile/me",
            json={
                "sex": "male",
                "birthdate": "1990-01-01",
                "height_cm": 175.0,
                "weight_kg": 70.0,
                "meals_per_day": 3,
            },
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(TEST_USER_ID)
        assert data["sex"] == "male"
        assert data["birthdate"] == "1990-01-01"
        assert data["height_cm"] == 175.0
        assert data["weight_kg"] == 70.0
        assert data["meals_per_day"] == 3

        # プロフィールがリポジトリに保存されていることを確認
        from app.domain.auth.value_objects import UserId

        saved_profile = profile_repo.get_by_user_id(UserId(str(TEST_USER_ID)))
        assert saved_profile is not None
        assert saved_profile.sex.value == "male"
        assert saved_profile.height_cm.value == 175.0

    def test_upsert_my_profile_update(
        self,
        client: TestClient,
        profile_repo: InMemoryProfileRepository,
        authenticated_user: tuple[User, TokenPair],
        clock: FixedClock,
    ):
        """正常系: 既存プロフィールの更新"""
        user, tokens = authenticated_user

        # 既存のプロフィールを作成
        from app.domain.profile.entities import Profile
        from app.domain.profile.value_objects import HeightCm, WeightKg, Sex

        existing_profile = Profile(
            user_id=user.id,
            sex=Sex.MALE,
            birthdate=date(1990, 1, 1),
            height_cm=HeightCm(175.0),
            weight_kg=WeightKg(70.0),
            image_id=None,
            meals_per_day=3,
            created_at=clock.now(),
            updated_at=clock.now(),
        )
        profile_repo.save(existing_profile)

        # プロフィールを更新
        response = client.put(
            "/api/v1/profile/me",
            json={
                "sex": "female",
                "birthdate": "1995-05-15",
                "height_cm": 160.0,
                "weight_kg": 55.0,
                "meals_per_day": 4,
            },
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["sex"] == "female"
        assert data["birthdate"] == "1995-05-15"
        assert data["height_cm"] == 160.0
        assert data["weight_kg"] == 55.0
        assert data["meals_per_day"] == 4

        # プロフィールが更新されていることを確認
        from app.domain.auth.value_objects import UserId

        updated_profile = profile_repo.get_by_user_id(
            UserId(str(TEST_USER_ID)))
        assert updated_profile is not None
        assert updated_profile.sex.value == "female"
        assert updated_profile.height_cm.value == 160.0

    def test_upsert_my_profile_without_meals_per_day(
        self,
        client: TestClient,
        authenticated_user,
    ):
        """正常系: meals_per_dayを省略した場合"""
        _, tokens = authenticated_user

        response = client.put(
            "/api/v1/profile/me",
            json={
                "sex": "male",
                "birthdate": "1990-01-01",
                "height_cm": 175.0,
                "weight_kg": 70.0,
            },
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["meals_per_day"] is None

    def test_upsert_my_profile_unauthorized(self, client: TestClient):
        """異常系: トークンがない場合"""
        response = client.put(
            "/api/v1/profile/me",
            json={
                "sex": "male",
                "birthdate": "1990-01-01",
                "height_cm": 175.0,
                "weight_kg": 70.0,
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    def test_upsert_my_profile_invalid_height(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """異常系: 無効な身長（負の値）"""
        _, tokens = authenticated_user

        response = client.put(
            "/api/v1/profile/me",
            json={
                "sex": "male",
                "birthdate": "1990-01-01",
                "height_cm": -10.0,  # 無効な値
                "weight_kg": 70.0,
            },
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_upsert_my_profile_invalid_weight(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """異常系: 無効な体重（負の値）"""
        _, tokens = authenticated_user

        response = client.put(
            "/api/v1/profile/me",
            json={
                "sex": "male",
                "birthdate": "1990-01-01",
                "height_cm": 175.0,
                "weight_kg": -10.0,  # 無効な値
            },
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
