from __future__ import annotations

import uuid
from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.domain.auth.entities import User
from app.application.auth.ports.token_service_port import TokenPair
from app.di.container import (
    get_activate_target_use_case,
    get_create_target_use_case,
    get_current_user_use_case,
    get_get_active_target_use_case,
    get_get_target_use_case,
    get_list_targets_use_case,
    get_profile_query_service,
    get_target_generator,
    get_target_uow,
    get_token_service,
    get_update_target_use_case,
)
from app.main import create_app
from app.application.auth.use_cases.current_user.get_current_user import (
    GetCurrentUserUseCase,
)
from app.application.profile.use_cases.get_my_profile import GetMyProfileUseCase
from app.application.profile.ports.profile_query_port import ProfileQueryPort
from app.infra.profile.profile_query_service import ProfileQueryService
from app.application.target.use_cases.activate_target import ActivateTargetUseCase
from app.application.target.use_cases.create_target import CreateTargetUseCase
from app.application.target.use_cases.get_active_target import GetActiveTargetUseCase
from app.application.target.use_cases.get_target import GetTargetUseCase
from app.application.target.use_cases.list_targets import ListTargetsUseCase
from app.application.target.use_cases.update_target import UpdateTargetUseCase
from tests.fakes.auth_repositories import InMemoryUserRepository
from tests.fakes.auth_services import FakePasswordHasher, FakeTokenService, FixedClock
from tests.fakes.auth_uow import FakeAuthUnitOfWork
from tests.fakes.profile_repositories import InMemoryProfileRepository
from tests.fakes.profile_uow import FakeProfileUnitOfWork
from app.infra.storage.profile_image_storage import InMemoryProfileImageStorage
from tests.unit.application.target.fakes import (
    FakeTargetRepository,
    FakeTargetSnapshotRepository,
    FakeTargetUnitOfWork,
    FakeTargetGenerator,
)

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
def target_repo() -> FakeTargetRepository:
    """テスト用のFakeTargetRepository"""
    return FakeTargetRepository()


@pytest.fixture
def target_snapshot_repo() -> FakeTargetSnapshotRepository:
    """テスト用のFakeTargetSnapshotRepository"""
    return FakeTargetSnapshotRepository()


@pytest.fixture
def target_uow(
    target_repo: FakeTargetRepository,
    target_snapshot_repo: FakeTargetSnapshotRepository,
) -> FakeTargetUnitOfWork:
    """テスト用のFakeTargetUnitOfWork"""
    return FakeTargetUnitOfWork(
        target_repo=target_repo,
        target_snapshot_repo=target_snapshot_repo,
    )


@pytest.fixture
def target_generator() -> FakeTargetGenerator:
    """テスト用のFakeTargetGenerator"""
    return FakeTargetGenerator()


@pytest.fixture
def app(
    user_repo: InMemoryUserRepository,
    password_hasher: FakePasswordHasher,
    token_service: FakeTokenService,
    clock: FixedClock,
    auth_uow: FakeAuthUnitOfWork,
    profile_uow: FakeProfileUnitOfWork,
    profile_image_storage: InMemoryProfileImageStorage,
    target_uow: FakeTargetUnitOfWork,
    target_generator: FakeTargetGenerator,
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

    # ProfileQueryServiceを作成（GetMyProfileUseCaseを使う）
    profile_query_service: ProfileQueryPort = ProfileQueryService(
        get_my_profile_uc=my_profile_use_case,
    )

    create_target_use_case = CreateTargetUseCase(
        uow=target_uow,
        generator=target_generator,
        profile_query=profile_query_service,
        clock=clock,
    )

    list_targets_use_case = ListTargetsUseCase(
        uow=target_uow,
    )

    get_active_target_use_case = GetActiveTargetUseCase(
        uow=target_uow,
    )

    get_target_use_case = GetTargetUseCase(
        uow=target_uow,
    )

    update_target_use_case = UpdateTargetUseCase(
        uow=target_uow,
    )

    activate_target_use_case = ActivateTargetUseCase(
        uow=target_uow,
    )

    # DIをオーバーライド
    app.dependency_overrides[get_current_user_use_case] = lambda: current_user_use_case
    app.dependency_overrides[get_token_service] = lambda: token_service
    app.dependency_overrides[get_target_uow] = lambda: target_uow
    app.dependency_overrides[get_target_generator] = lambda: target_generator
    app.dependency_overrides[get_profile_query_service] = lambda: profile_query_service
    app.dependency_overrides[get_create_target_use_case] = lambda: create_target_use_case
    app.dependency_overrides[get_list_targets_use_case] = lambda: list_targets_use_case
    app.dependency_overrides[get_get_active_target_use_case] = lambda: get_active_target_use_case
    app.dependency_overrides[get_get_target_use_case] = lambda: get_target_use_case
    app.dependency_overrides[get_update_target_use_case] = lambda: update_target_use_case
    app.dependency_overrides[get_activate_target_use_case] = lambda: activate_target_use_case

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
) -> tuple[User, TokenPair]:
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


@pytest.fixture
def profile_setup(
    profile_repo: InMemoryProfileRepository,
    authenticated_user: tuple[User, TokenPair],
    clock: FixedClock,
):
    """プロフィールを作成するヘルパー"""
    user, _ = authenticated_user

    from app.domain.profile.entities import Profile
    from app.domain.profile.value_objects import HeightCm, WeightKg, Sex

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
    return profile


class TestCreateTarget:
    """POST /targets のテスト"""

    def test_create_target_success(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
        profile_setup,
    ):
        """正常系: ターゲット作成が成功する"""
        _, tokens = authenticated_user

        response = client.post(
            "/api/v1/targets",
            json={
                "title": "My Target",
                "goal_type": "weight_loss",
                "goal_description": "Lose 5kg",
                "activity_level": "normal",
            },
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "My Target"
        assert data["goal_type"] == "weight_loss"
        assert data["activity_level"] == "normal"
        assert "nutrients" in data
        assert len(data["nutrients"]) > 0

    def test_create_target_without_profile(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """異常系: プロフィールがない場合"""
        _, tokens = authenticated_user

        response = client.post(
            "/api/v1/targets",
            json={
                "title": "My Target",
                "goal_type": "weight_loss",
                "goal_description": "Lose 5kg",
                "activity_level": "normal",
            },
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        # ProfileNotFoundErrorはProfileNotFoundErrorとして扱われ、404が返る
        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_create_target_limit_exceeded(
        self,
        client: TestClient,
        target_repo: FakeTargetRepository,
        authenticated_user: tuple[User, TokenPair],
        profile_setup,
        clock: FixedClock,
    ):
        """異常系: ターゲット上限超過（5個以上）"""
        _, tokens = authenticated_user

        # 既に5個のターゲットを作成
        from tests.unit.application.target.fakes import make_target
        from app.domain.auth.value_objects import UserId

        for i in range(5):
            target = make_target(
                str(TEST_USER_ID),
                title=f"Target {i}",
                created_at=clock.now(),
            )
            target_repo.add(target)

        response = client.post(
            "/api/v1/targets",
            json={
                "title": "My Target",
                "goal_type": "weight_loss",
                "goal_description": "Lose 5kg",
                "activity_level": "normal",
            },
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 409
        data = response.json()
        assert "error" in data

    def test_create_target_unauthorized(self, client: TestClient):
        """異常系: トークンがない場合"""
        response = client.post(
            "/api/v1/targets",
            json={
                "title": "My Target",
                "goal_type": "weight_loss",
                "goal_description": "Lose 5kg",
                "activity_level": "normal",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestListTargets:
    """GET /targets のテスト"""

    def test_list_targets_success(
        self,
        client: TestClient,
        target_repo: FakeTargetRepository,
        authenticated_user: tuple[User, TokenPair],
        clock: FixedClock,
    ):
        """正常系: ターゲット一覧取得が成功する"""
        _, tokens = authenticated_user

        # ターゲットを作成
        from tests.unit.application.target.fakes import make_target

        target1 = make_target(
            str(TEST_USER_ID),
            title="Target 1",
            created_at=clock.now(),
        )
        target2 = make_target(
            str(TEST_USER_ID),
            title="Target 2",
            created_at=clock.now(),
        )
        target_repo.add(target1)
        target_repo.add(target2)

        response = client.get(
            "/api/v1/targets",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 2

    def test_list_targets_empty(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """正常系: ターゲットが0件の場合"""
        _, tokens = authenticated_user

        response = client.get(
            "/api/v1/targets",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 0

    def test_list_targets_with_pagination(
        self,
        client: TestClient,
        target_repo: FakeTargetRepository,
        authenticated_user: tuple[User, TokenPair],
        clock: FixedClock,
    ):
        """正常系: ページングが機能する"""
        _, tokens = authenticated_user

        # 3個のターゲットを作成
        from tests.unit.application.target.fakes import make_target

        for i in range(3):
            target = make_target(
                str(TEST_USER_ID),
                title=f"Target {i}",
                created_at=clock.now(),
            )
            target_repo.add(target)

        # limit=2で取得
        response = client.get(
            "/api/v1/targets?limit=2",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 2

    def test_list_targets_unauthorized(self, client: TestClient):
        """異常系: トークンがない場合"""
        response = client.get("/api/v1/targets")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestGetActiveTarget:
    """GET /targets/active のテスト"""

    def test_get_active_target_success(
        self,
        client: TestClient,
        target_repo: FakeTargetRepository,
        authenticated_user: tuple[User, TokenPair],
        clock: FixedClock,
    ):
        """正常系: アクティブターゲット取得が成功する"""
        _, tokens = authenticated_user

        # アクティブなターゲットを作成
        from tests.unit.application.target.fakes import make_target

        target = make_target(
            str(TEST_USER_ID),
            title="Active Target",
            is_active=True,
            created_at=clock.now(),
        )
        target_repo.add(target)

        response = client.get(
            "/api/v1/targets/active",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Active Target"
        assert data["is_active"] is True

    def test_get_active_target_not_found(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """異常系: アクティブターゲットがない場合"""
        _, tokens = authenticated_user

        response = client.get(
            "/api/v1/targets/active",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_get_active_target_unauthorized(self, client: TestClient):
        """異常系: トークンがない場合"""
        response = client.get("/api/v1/targets/active")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestGetTarget:
    """GET /targets/{target_id} のテスト"""

    def test_get_target_success(
        self,
        client: TestClient,
        target_repo: FakeTargetRepository,
        authenticated_user: tuple[User, TokenPair],
        clock: FixedClock,
    ):
        """正常系: ターゲット1件取得が成功する"""
        _, tokens = authenticated_user

        # ターゲットを作成
        from tests.unit.application.target.fakes import make_target

        target = make_target(
            str(TEST_USER_ID),
            title="My Target",
            created_at=clock.now(),
        )
        target_repo.add(target)
        target_id = str(target.id.value)

        response = client.get(
            f"/api/v1/targets/{target_id}",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "My Target"
        assert data["id"] == target_id

    def test_get_target_not_found(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """異常系: ターゲットが存在しない場合"""
        _, tokens = authenticated_user

        response = client.get(
            "/api/v1/targets/non-existent-id",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_get_target_unauthorized(self, client: TestClient):
        """異常系: トークンがない場合"""
        response = client.get("/api/v1/targets/some-id")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestUpdateTarget:
    """PATCH /targets/{target_id} のテスト"""

    def test_update_target_success(
        self,
        client: TestClient,
        target_repo: FakeTargetRepository,
        authenticated_user: tuple[User, TokenPair],
        clock: FixedClock,
    ):
        """正常系: ターゲット更新が成功する"""
        _, tokens = authenticated_user

        # ターゲットを作成
        from tests.unit.application.target.fakes import make_target

        target = make_target(
            str(TEST_USER_ID),
            title="Original Title",
            created_at=clock.now(),
        )
        target_repo.add(target)
        target_id = str(target.id.value)

        response = client.patch(
            f"/api/v1/targets/{target_id}",
            json={
                "title": "Updated Title",
            },
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_update_target_not_found(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """異常系: ターゲットが存在しない場合"""
        _, tokens = authenticated_user

        response = client.patch(
            "/api/v1/targets/non-existent-id",
            json={
                "title": "Updated Title",
            },
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_update_target_unauthorized(self, client: TestClient):
        """異常系: トークンがない場合"""
        response = client.patch(
            "/api/v1/targets/some-id",
            json={
                "title": "Updated Title",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestActivateTarget:
    """POST /targets/{target_id}/activate のテスト"""

    def test_activate_target_success(
        self,
        client: TestClient,
        target_repo: FakeTargetRepository,
        authenticated_user: tuple[User, TokenPair],
        clock: FixedClock,
    ):
        """正常系: ターゲットアクティブ化が成功する"""
        _, tokens = authenticated_user

        # 2個のターゲットを作成（1つ目をアクティブに）
        from tests.unit.application.target.fakes import make_target

        target1 = make_target(
            str(TEST_USER_ID),
            title="Target 1",
            is_active=True,
            created_at=clock.now(),
        )
        target2 = make_target(
            str(TEST_USER_ID),
            title="Target 2",
            is_active=False,
            created_at=clock.now(),
        )
        target_repo.add(target1)
        target_repo.add(target2)
        target2_id = str(target2.id.value)

        response = client.post(
            f"/api/v1/targets/{target2_id}/activate",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True
        assert data["id"] == target2_id

        # target1が非アクティブになっていることを確認
        assert not target1.is_active

    def test_activate_target_not_found(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """異常系: ターゲットが存在しない場合"""
        _, tokens = authenticated_user

        response = client.post(
            "/api/v1/targets/non-existent-id/activate",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_activate_target_unauthorized(self, client: TestClient):
        """異常系: トークンがない場合"""
        response = client.post("/api/v1/targets/some-id/activate")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data
