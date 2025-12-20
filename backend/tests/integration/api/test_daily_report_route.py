from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import create_app
from app.domain.auth.entities import User
from app.application.auth.ports.token_service_port import TokenPair
from app.application.auth.use_cases.current_user.get_current_user import GetCurrentUserUseCase
from app.application.meal.use_cases.check_daily_log_completion import CheckDailyLogCompletionUseCase
from app.application.nutrition.use_cases.compute_daily_nutrition import ComputeDailyNutritionSummaryUseCase
from app.application.nutrition.use_cases.generate_daily_nutrition_report import GenerateDailyNutritionReportUseCase
from app.application.nutrition.use_cases.get_daily_nutrition_report import GetDailyNutritionReportUseCase
from app.application.profile.ports.profile_query_port import ProfileForDailyLog, ProfileQueryPort
from app.application.target.use_cases.ensure_daily_snapshot import EnsureDailyTargetSnapshotUseCase

from app.di.container import (
    get_check_daily_log_completion_use_case,
    get_compute_daily_nutrition_summary_use_case,
    get_current_user_use_case,
    get_daily_nutrition_report_generator,
    get_ensure_daily_target_snapshot_use_case,
    get_generate_daily_nutrition_report_use_case,
    get_get_daily_nutrition_report_use_case,
    get_meal_uow,
    get_nutrition_uow,
    get_plan_checker,
    get_profile_query_service,
    get_target_uow,
    get_token_service,
)

from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.meal.value_objects import FoodEntryId, MealType
from app.domain.target.entities import TargetDefinition, TargetNutrient
from app.domain.target.value_objects import (
    ActivityLevel,
    GoalType,
    NutrientAmount,
    NutrientCode,
    NutrientSource,
    TargetId,
)

from tests.fakes.auth_repositories import InMemoryUserRepository
from tests.fakes.auth_services import FakePasswordHasher, FakeTokenService, FixedClock
from tests.fakes.auth_uow import FakeAuthUnitOfWork
from tests.fakes.meal_uow import FakeMealUnitOfWork
from tests.unit.application.nutrition.fakes import (
    FakeDailyNutritionReportGenerator,
    FakeDailyNutritionReportRepository,
    FakeDailyNutritionRepository,
    FakeMealNutritionRepository,
    FakeNutritionUnitOfWork,
    FakePlanChecker,
)
from tests.unit.application.target.fakes import (
    FakeTargetRepository,
    FakeTargetSnapshotRepository,
    FakeTargetUnitOfWork,
)

# =========================================
# Constants
# =========================================

TEST_USER_ID = uuid.UUID("12345678-1234-5678-1234-567812345678")
TARGET_DATE = date(2024, 1, 1)
TARGET_DATE_STR = "2024-01-01"


# =========================================
# Helper Functions
# =========================================

def _assert_error(resp, *, status_code: int, code: str) -> None:
    """エラーレスポンスのアサーション"""
    assert resp.status_code == status_code
    data = resp.json()
    assert "error" in data
    assert isinstance(data["error"], dict)
    assert data["error"]["code"] == code
    assert "message" in data["error"]


# =========================================
# Fake Repositories
# =========================================

class FakeFoodEntryRepository:
    """インメモリのFoodEntryRepository"""

    def __init__(self) -> None:
        self._entries: list[FoodEntry] = []

    def add(self, entry: FoodEntry) -> None:
        self._entries.append(entry)

    def list_by_user_and_date(self, *, user_id: UserId, target_date: date) -> Sequence[FoodEntry]:
        user_id_value = getattr(user_id, "value", str(user_id))
        return [
            e for e in self._entries
            if getattr(e.user_id, "value", str(e.user_id)) == user_id_value
            and e.date == target_date
            and e.deleted_at is None
        ]


class FakeProfileQuery(ProfileQueryPort):
    """テスト用のProfileQueryPort実装"""

    def __init__(self) -> None:
        self._daily_log: ProfileForDailyLog | None = None

    def set_daily_log_profile(self, meals_per_day: int) -> None:
        """テスト用: プロフィール情報を設定"""
        self._daily_log = ProfileForDailyLog(meals_per_day=meals_per_day)

    def get_profile_for_daily_log(self, user_id: UserId) -> ProfileForDailyLog | None:
        return self._daily_log

    def get_profile_for_target(self, user_id: UserId):
        return None

    def get_profile_for_recommendation(self, user_id: UserId):
        return None


# =========================================
# Fixtures
# =========================================

@pytest.fixture
def user_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def password_hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


@pytest.fixture
def token_service() -> FakeTokenService:
    return FakeTokenService()


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock()


@pytest.fixture
def auth_uow(user_repo: InMemoryUserRepository) -> FakeAuthUnitOfWork:
    return FakeAuthUnitOfWork(user_repo=user_repo)


@pytest.fixture
def food_entry_repo() -> FakeFoodEntryRepository:
    return FakeFoodEntryRepository()


@pytest.fixture
def meal_uow(food_entry_repo: FakeFoodEntryRepository) -> FakeMealUnitOfWork:
    return FakeMealUnitOfWork(food_entry_repo=food_entry_repo)


@pytest.fixture
def profile_query() -> FakeProfileQuery:
    return FakeProfileQuery()


@pytest.fixture
def daily_report_repo() -> FakeDailyNutritionReportRepository:
    return FakeDailyNutritionReportRepository()


@pytest.fixture
def nutrition_uow(daily_report_repo: FakeDailyNutritionReportRepository) -> FakeNutritionUnitOfWork:
    return FakeNutritionUnitOfWork(
        meal_nutrition_repo=FakeMealNutritionRepository(),
        daily_nutrition_repo=FakeDailyNutritionRepository(),
        daily_report_repo=daily_report_repo,
    )


@pytest.fixture
def plan_checker() -> FakePlanChecker:
    return FakePlanChecker()


@pytest.fixture
def report_generator() -> FakeDailyNutritionReportGenerator:
    return FakeDailyNutritionReportGenerator()


@pytest.fixture
def target_uow() -> FakeTargetUnitOfWork:
    return FakeTargetUnitOfWork(
        target_repo=FakeTargetRepository(),
        target_snapshot_repo=FakeTargetSnapshotRepository(),
    )


@pytest.fixture
def app(
    auth_uow: FakeAuthUnitOfWork,
    token_service: FakeTokenService,
    clock: FixedClock,
    meal_uow: FakeMealUnitOfWork,
    nutrition_uow: FakeNutritionUnitOfWork,
    plan_checker: FakePlanChecker,
    profile_query: FakeProfileQuery,
    target_uow: FakeTargetUnitOfWork,
    report_generator: FakeDailyNutritionReportGenerator,
) -> FastAPI:
    """FAKEを使ったDIオーバーライドでFastAPIアプリを作成"""
    app = create_app()

    # UseCaseをFAKEで作成
    current_user_uc = GetCurrentUserUseCase(uow=auth_uow)

    check_daily_log_uc = CheckDailyLogCompletionUseCase(
        profile_query=profile_query,
        meal_uow=meal_uow,
    )

    compute_daily_nutrition_uc = ComputeDailyNutritionSummaryUseCase(
        uow=nutrition_uow,
        plan_checker=plan_checker,
    )

    ensure_target_snapshot_uc = EnsureDailyTargetSnapshotUseCase(
        uow=target_uow,
    )

    generate_report_uc = GenerateDailyNutritionReportUseCase(
        daily_log_uc=check_daily_log_uc,
        profile_query=profile_query,
        ensure_target_snapshot_uc=ensure_target_snapshot_uc,
        daily_nutrition_uc=compute_daily_nutrition_uc,
        nutrition_uow=nutrition_uow,
        report_generator=report_generator,
        clock=clock,
        plan_checker=plan_checker,
    )

    get_report_uc = GetDailyNutritionReportUseCase(uow=nutrition_uow)

    # dependency_overrides
    app.dependency_overrides[get_current_user_use_case] = lambda: current_user_uc
    app.dependency_overrides[get_token_service] = lambda: token_service

    app.dependency_overrides[get_meal_uow] = lambda: meal_uow
    app.dependency_overrides[get_nutrition_uow] = lambda: nutrition_uow
    app.dependency_overrides[get_plan_checker] = lambda: plan_checker
    app.dependency_overrides[get_profile_query_service] = lambda: profile_query
    app.dependency_overrides[get_target_uow] = lambda: target_uow
    app.dependency_overrides[get_daily_nutrition_report_generator] = lambda: report_generator

    app.dependency_overrides[get_check_daily_log_completion_use_case] = lambda: check_daily_log_uc
    app.dependency_overrides[get_compute_daily_nutrition_summary_use_case] = lambda: compute_daily_nutrition_uc
    app.dependency_overrides[get_ensure_daily_target_snapshot_use_case] = lambda: ensure_target_snapshot_uc
    app.dependency_overrides[get_generate_daily_nutrition_report_use_case] = lambda: generate_report_uc
    app.dependency_overrides[get_get_daily_nutrition_report_use_case] = lambda: get_report_uc

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture
def authenticated_user(
    user_repo: InMemoryUserRepository,
    password_hasher: FakePasswordHasher,
    token_service: FakeTokenService,
    clock: FixedClock,
) -> tuple[User, TokenPair]:
    """認証済みユーザーとトークンを作成するヘルパー"""
    from app.domain.auth.value_objects import EmailAddress, TrialInfo, UserPlan
    from app.application.auth.ports.token_service_port import TokenPayload

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

    tokens = token_service.issue_tokens(
        TokenPayload(user_id=str(TEST_USER_ID), plan=user.plan)
    )

    return user, tokens


@pytest.fixture
def authed_client(client: TestClient, authenticated_user):
    """認証済みのTestClient"""
    _, tokens = authenticated_user
    client.cookies.set("ACCESS_TOKEN", tokens.access_token)
    return client


@pytest.fixture
def active_target(
    target_uow: FakeTargetUnitOfWork,
    authenticated_user: tuple[User, TokenPair],
    clock: FixedClock,
) -> TargetDefinition:
    """アクティブなターゲットを作成"""
    user, _ = authenticated_user

    target = TargetDefinition(
        id=TargetId(str(uuid.uuid4())),
        user_id=user.id,
        title="Test Target",
        goal_type=GoalType.WEIGHT_LOSS,
        goal_description=None,
        activity_level=ActivityLevel.NORMAL,
        nutrients=[
            TargetNutrient(
                code=code,
                amount=NutrientAmount(value=100.0, unit="g"),
                source=NutrientSource("llm"),
            )
            for code in NutrientCode
        ],
        is_active=True,
        created_at=clock.now(),
        updated_at=clock.now(),
        llm_rationale=None,
        disclaimer=None,
    )

    target_uow.target_repo.add(target)
    return target


def _add_main_entries(
    *,
    food_entry_repo: FakeFoodEntryRepository,
    user_id: UserId,
    clock: FixedClock,
    meals_per_day: int,
) -> None:
    """メインの食事エントリを追加するヘルパー"""
    for meal_index in range(1, meals_per_day + 1):
        entry = FoodEntry(
            id=FoodEntryId.new(),
            user_id=user_id,
            date=TARGET_DATE,
            meal_type=MealType.MAIN,
            meal_index=meal_index,
            name=f"Meal {meal_index}",
            amount_value=200.0,
            amount_unit="g",
            serving_count=None,
            note=None,
            created_at=clock.now(),
            updated_at=clock.now(),
            deleted_at=None,
        )
        food_entry_repo.add(entry)


# =========================================
# Tests
# =========================================

class TestGenerateDailyNutritionReport:
    """POST /api/v1/nutrition/daily/report のテスト"""

    def test_success(
        self,
        authed_client: TestClient,
        food_entry_repo: FakeFoodEntryRepository,
        nutrition_uow: FakeNutritionUnitOfWork,
        profile_query: FakeProfileQuery,
        authenticated_user,
        active_target: TargetDefinition,
        clock: FixedClock,
    ):
        """正常系: レポート生成が成功する"""
        user, _ = authenticated_user

        profile_query.set_daily_log_profile(meals_per_day=3)
        _add_main_entries(
            food_entry_repo=food_entry_repo,
            user_id=user.id,
            clock=clock,
            meals_per_day=3,
        )

        resp = authed_client.post(
            "/api/v1/nutrition/daily/report",
            json={"date": TARGET_DATE_STR},
        )
        assert resp.status_code == 201
        data = resp.json()

        assert data["date"] == TARGET_DATE_STR
        assert isinstance(data["summary"], str) and data["summary"]
        assert isinstance(data["good_points"], list) and data["good_points"]
        assert isinstance(data["improvement_points"],
                          list) and data["improvement_points"]
        assert isinstance(data["tomorrow_focus"],
                          list) and data["tomorrow_focus"]
        assert isinstance(data["created_at"], str) and data["created_at"]

        # 保存されていることを確認
        saved = nutrition_uow.daily_report_repo.get_by_user_and_date(
            user_id=user.id,
            target_date=TARGET_DATE,
        )
        assert saved is not None
        assert saved.summary == data["summary"]

    def test_not_completed(
        self,
        authed_client: TestClient,
        profile_query: FakeProfileQuery,
        active_target: TargetDefinition,
    ):
        """異常系: 食事ログが完了していない場合"""
        profile_query.set_daily_log_profile(meals_per_day=3)

        resp = authed_client.post(
            "/api/v1/nutrition/daily/report",
            json={"date": TARGET_DATE_STR},
        )
        _assert_error(resp, status_code=400, code="DAILY_LOG_NOT_COMPLETED")

    def test_already_exists(
        self,
        authed_client: TestClient,
        food_entry_repo: FakeFoodEntryRepository,
        nutrition_uow: FakeNutritionUnitOfWork,
        profile_query: FakeProfileQuery,
        authenticated_user,
        active_target: TargetDefinition,
        clock: FixedClock,
    ):
        """異常系: 既にレポートが存在する場合"""
        from app.domain.nutrition.daily_report import DailyNutritionReport

        user, _ = authenticated_user
        profile_query.set_daily_log_profile(meals_per_day=3)
        _add_main_entries(
            food_entry_repo=food_entry_repo,
            user_id=user.id,
            clock=clock,
            meals_per_day=3,
        )

        # 既存のレポートを作成
        existing = DailyNutritionReport.create(
            user_id=user.id,
            date=TARGET_DATE,
            summary="Existing report",
            good_points=["Good"],
            improvement_points=["Improve"],
            tomorrow_focus=["Focus"],
            created_at=clock.now(),
        )
        nutrition_uow.daily_report_repo.save(existing)

        resp = authed_client.post(
            "/api/v1/nutrition/daily/report",
            json={"date": TARGET_DATE_STR},
        )
        _assert_error(resp, status_code=409,
                      code="DAILY_NUTRITION_REPORT_ALREADY_EXISTS")

    def test_profile_not_found(
        self,
        authed_client: TestClient,
        active_target: TargetDefinition,
    ):
        """異常系: プロフィールが存在しない場合"""
        resp = authed_client.post(
            "/api/v1/nutrition/daily/report",
            json={"date": TARGET_DATE_STR},
        )
        _assert_error(resp, status_code=400,
                      code="DAILY_LOG_PROFILE_NOT_FOUND")

    def test_invalid_date_format(self, authed_client: TestClient):
        """異常系: 無効な日付フォーマット"""
        resp = authed_client.post(
            "/api/v1/nutrition/daily/report",
            json={"date": "invalid-date"},
        )
        _assert_error(resp, status_code=400, code="VALIDATION_ERROR")

    def test_missing_date(self, authed_client: TestClient):
        """異常系: 日付が指定されていない場合"""
        resp = authed_client.post(
            "/api/v1/nutrition/daily/report",
            json={},
        )
        _assert_error(resp, status_code=400, code="VALIDATION_ERROR")

    def test_unauthorized(self, client: TestClient):
        """異常系: 認証されていない場合"""
        resp = client.post(
            "/api/v1/nutrition/daily/report",
            json={"date": TARGET_DATE_STR},
        )
        assert resp.status_code == 401
        assert "error" in resp.json()

    def test_invalid_token(self, client: TestClient):
        """異常系: 無効なトークンの場合"""
        client.cookies.set("ACCESS_TOKEN", "invalid-token")
        resp = client.post(
            "/api/v1/nutrition/daily/report",
            json={"date": TARGET_DATE_STR},
        )
        assert resp.status_code == 401
        assert "error" in resp.json()


class TestGetDailyNutritionReport:
    """GET /api/v1/nutrition/daily/report のテスト"""

    def test_success(
        self,
        authed_client: TestClient,
        nutrition_uow: FakeNutritionUnitOfWork,
        authenticated_user,
        clock: FixedClock,
    ):
        """正常系: レポート取得が成功する"""
        from app.domain.nutrition.daily_report import DailyNutritionReport

        user, _ = authenticated_user
        report = DailyNutritionReport.create(
            user_id=user.id,
            date=TARGET_DATE,
            summary="Test summary",
            good_points=["Good 1", "Good 2"],
            improvement_points=["Improve 1"],
            tomorrow_focus=["Focus 1", "Focus 2"],
            created_at=clock.now(),
        )
        nutrition_uow.daily_report_repo.save(report)

        resp = authed_client.get(
            f"/api/v1/nutrition/daily/report?date={TARGET_DATE_STR}"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["date"] == TARGET_DATE_STR
        assert data["summary"] == "Test summary"
        assert data["good_points"] == ["Good 1", "Good 2"]
        assert data["improvement_points"] == ["Improve 1"]
        assert data["tomorrow_focus"] == ["Focus 1", "Focus 2"]
        assert isinstance(data["created_at"], str) and data["created_at"]

    def test_not_found(self, authed_client: TestClient):
        """異常系: レポートが存在しない場合"""
        resp = authed_client.get(
            f"/api/v1/nutrition/daily/report?date={TARGET_DATE_STR}"
        )
        assert resp.status_code == 404
        data = resp.json()
        assert ("detail" in data) or ("error" in data)

    def test_missing_date(self, authed_client: TestClient):
        """異常系: 日付が指定されていない場合"""
        resp = authed_client.get("/api/v1/nutrition/daily/report")
        _assert_error(resp, status_code=400, code="VALIDATION_ERROR")

    def test_invalid_date_format(self, authed_client: TestClient):
        """異常系: 無効な日付フォーマット"""
        resp = authed_client.get(
            "/api/v1/nutrition/daily/report?date=invalid-date"
        )
        _assert_error(resp, status_code=400, code="VALIDATION_ERROR")

    def test_different_user_cannot_see_other_users_report(
        self,
        authed_client: TestClient,
        nutrition_uow: FakeNutritionUnitOfWork,
        user_repo: InMemoryUserRepository,
        password_hasher: FakePasswordHasher,
        clock: FixedClock,
    ):
        """異常系: 他のユーザーのレポートは見られない"""
        from app.domain.auth.value_objects import EmailAddress, TrialInfo, UserPlan
        from app.domain.nutrition.daily_report import DailyNutritionReport

        # user2 を作成
        user2 = User(
            id=UserId(str(uuid.uuid4())),
            email=EmailAddress("user2@example.com"),
            hashed_password=password_hasher.hash("password123"),
            name="User 2",
            plan=UserPlan.TRIAL,
            trial_info=TrialInfo(trial_ends_at=None),
            has_profile=False,
            created_at=clock.now(),
        )
        user_repo.save(user2)

        # user2のレポートを作成
        report2 = DailyNutritionReport.create(
            user_id=user2.id,
            date=TARGET_DATE,
            summary="User2 report",
            good_points=["Good"],
            improvement_points=["Improve"],
            tomorrow_focus=["Focus"],
            created_at=clock.now(),
        )
        nutrition_uow.daily_report_repo.save(report2)

        # 認証済みユーザー（user1）でuser2のレポートを取得しようとする
        resp = authed_client.get(
            f"/api/v1/nutrition/daily/report?date={TARGET_DATE_STR}"
        )
        assert resp.status_code == 404

    def test_unauthorized(self, client: TestClient):
        """異常系: 認証されていない場合"""
        resp = client.get(
            f"/api/v1/nutrition/daily/report?date={TARGET_DATE_STR}"
        )
        assert resp.status_code == 401
        assert "error" in resp.json()

    def test_invalid_token(self, client: TestClient):
        """異常系: 無効なトークンの場合"""
        client.cookies.set("ACCESS_TOKEN", "invalid-token")
        resp = client.get(
            f"/api/v1/nutrition/daily/report?date={TARGET_DATE_STR}"
        )
        assert resp.status_code == 401
        assert "error" in resp.json()
