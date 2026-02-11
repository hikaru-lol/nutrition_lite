from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.domain.auth.entities import User
from app.application.auth.ports.token_service_port import TokenPair
from app.di.container import (
    get_compute_daily_nutrition_summary_use_case,
    get_compute_meal_nutrition_use_case,
    get_current_user_use_case,
    get_meal_entry_query_service,
    get_meal_uow,
    get_nutrition_estimator,
    get_nutrition_uow,
    get_plan_checker,
    get_token_service,
)
from app.main import create_app
from app.application.auth.use_cases.current_user.get_current_user import (
    GetCurrentUserUseCase,
)
from app.application.nutrition.use_cases.compute_daily_nutrition import (
    ComputeDailyNutritionSummaryUseCase,
)
from app.application.nutrition.use_cases.compute_meal_nutrition import (
    ComputeMealNutritionUseCase,
)
from app.application.nutrition.ports.meal_entry_query_port import MealEntryQueryPort
from app.application.nutrition.ports.nutrition_estimator_port import (
    NutritionEstimatorPort,
)
from app.application.nutrition.ports.meal_nutrition_repository_port import (
    MealNutritionSummaryRepositoryPort,
)
from app.application.nutrition.ports.daily_nutrition_repository_port import (
    DailyNutritionSummaryRepositoryPort,
)
from app.application.nutrition.ports.uow_port import DailyNutritionUnitOfWorkPort
from app.application.auth.ports.plan_checker_port import PlanCheckerPort
from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.meal.value_objects import MealType
from app.domain.nutrition.meal_nutrition import MealNutrientIntake
from app.domain.target.value_objects import NutrientCode, NutrientAmount
from tests.fakes.auth_repositories import InMemoryUserRepository
from tests.fakes.auth_services import FakePasswordHasher, FakeTokenService, FixedClock
from tests.fakes.auth_uow import FakeAuthUnitOfWork
from tests.fakes.meal_uow import FakeMealUnitOfWork
# test_meal_routeから必要なFAKE実装をインポート
from tests.integration.api.test_meal_route import (
    FakeFoodEntryRepository,
    FakeMealNutritionRepository,
    FakeDailyNutritionRepository,
    FakeNutritionUnitOfWork,
    FakePlanChecker,
)

# テスト用の固定UUID
TEST_USER_ID = uuid.UUID("12345678-1234-5678-1234-567812345678")


# =====================================================================
# Fake Implementations
# =====================================================================


class FakeMealEntryQueryService(MealEntryQueryPort):
    """インメモリのMealEntryQueryService"""

    def __init__(self, meal_uow: FakeMealUnitOfWork) -> None:
        self._meal_uow = meal_uow

    def list_entries_for_meal(
        self,
        user_id: UserId,
        date_: date,
        meal_type: MealType,
        meal_index: int | None,
    ) -> Sequence[FoodEntry]:
        with self._meal_uow as uow:
            return list(
                uow.food_entry_repo.list_by_user_date_type_index(
                    user_id=user_id,
                    target_date=date_,
                    meal_type=meal_type,
                    meal_index=meal_index,
                )
            )


class FakeNutritionEstimator(NutritionEstimatorPort):
    """インメモリのNutritionEstimator - 全ての栄養素を含む固定値を返す"""

    def estimate_for_entries(
        self,
        user_id: UserId,
        date: date,
        entries: Sequence[FoodEntry],
    ) -> list[MealNutrientIntake]:
        from app.domain.nutrition.meal_nutrition import MealNutrientIntake
        from app.domain.target.value_objects import NutrientSource

        # 簡単な固定値を返す（全ての栄養素を含む）
        total_amount = sum(
            e.amount_value or 0.0 for e in entries) if entries else 0.0
        source = NutrientSource("llm")

        # 全ての栄養素を含む必要がある（エントリが0件でも全て0で返す）
        return [
            MealNutrientIntake(
                code=NutrientCode.PROTEIN,
                amount=NutrientAmount(value=total_amount * 0.20, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.FAT,
                amount=NutrientAmount(value=total_amount * 0.10, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.CARBOHYDRATE,
                amount=NutrientAmount(value=total_amount * 0.50, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.WATER,
                amount=NutrientAmount(value=total_amount * 0.10, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.FIBER,
                amount=NutrientAmount(value=total_amount * 0.05, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.SODIUM,
                amount=NutrientAmount(value=total_amount * 0.05, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.IRON,
                amount=NutrientAmount(value=total_amount * 0.05, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.CALCIUM,
                amount=NutrientAmount(value=total_amount * 0.05, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.VITAMIN_D,
                amount=NutrientAmount(value=total_amount * 0.05, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.POTASSIUM,
                amount=NutrientAmount(value=total_amount * 0.05, unit="g"),
                source=source,
            ),
        ]


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
def food_entry_repo() -> FakeFoodEntryRepository:
    """テスト用のFakeFoodEntryRepository"""
    return FakeFoodEntryRepository()


@pytest.fixture
def meal_uow(food_entry_repo: FakeFoodEntryRepository) -> FakeMealUnitOfWork:
    """テスト用のFakeMealUnitOfWork"""
    return FakeMealUnitOfWork(food_entry_repo=food_entry_repo)


@pytest.fixture
def meal_nutrition_repo() -> FakeMealNutritionRepository:
    """テスト用のFakeMealNutritionRepository"""
    return FakeMealNutritionRepository()


@pytest.fixture
def daily_nutrition_repo() -> FakeDailyNutritionRepository:
    """テスト用のFakeDailyNutritionRepository"""
    return FakeDailyNutritionRepository()


@pytest.fixture
def nutrition_uow(
    meal_nutrition_repo: FakeMealNutritionRepository,
    daily_nutrition_repo: FakeDailyNutritionRepository,
) -> FakeNutritionUnitOfWork:
    """テスト用のFakeNutritionUnitOfWork"""
    return FakeNutritionUnitOfWork(
        meal_nutrition_repo=meal_nutrition_repo,
        daily_nutrition_repo=daily_nutrition_repo,
    )


@pytest.fixture
def plan_checker() -> FakePlanChecker:
    """テスト用のFakePlanChecker"""
    return FakePlanChecker()


@pytest.fixture
def meal_entry_query_service(
    meal_uow: FakeMealUnitOfWork,
) -> FakeMealEntryQueryService:
    """テスト用のFakeMealEntryQueryService"""
    return FakeMealEntryQueryService(meal_uow=meal_uow)


@pytest.fixture
def nutrition_estimator() -> FakeNutritionEstimator:
    """テスト用のFakeNutritionEstimator"""
    return FakeNutritionEstimator()


@pytest.fixture
def app(
    user_repo: InMemoryUserRepository,
    password_hasher: FakePasswordHasher,
    token_service: FakeTokenService,
    clock: FixedClock,
    auth_uow: FakeAuthUnitOfWork,
    meal_uow: FakeMealUnitOfWork,
    nutrition_uow: FakeNutritionUnitOfWork,
    plan_checker: FakePlanChecker,
    meal_entry_query_service: FakeMealEntryQueryService,
    nutrition_estimator: FakeNutritionEstimator,
) -> FastAPI:
    """
    FAKEを使ったDIオーバーライドでFastAPIアプリを作成
    """
    app = create_app()

    # UseCaseをFAKEで作成
    current_user_use_case = GetCurrentUserUseCase(
        uow=auth_uow,
    )

    # ComputeMealNutritionUseCaseをラップしてuser_idをUserIdに変換
    class FakeComputeMealNutritionUseCase:
        def __init__(self, real_uc: ComputeMealNutritionUseCase) -> None:
            self._real_uc = real_uc

        def execute(
            self,
            user_id: UserId | str,
            date_: date,
            meal_type_str: str,
            meal_index: int | None,
        ):
            # user_idがstrの場合はUserIdに変換
            if isinstance(user_id, str):
                user_id = UserId(user_id)
            return self._real_uc.execute(user_id, date_, meal_type_str, meal_index)

    # ComputeDailyNutritionSummaryUseCaseをラップしてuser_idをUserIdに変換
    class FakeComputeDailyNutritionSummaryUseCase:
        def __init__(self, real_uc: ComputeDailyNutritionSummaryUseCase) -> None:
            self._real_uc = real_uc

        def execute(self, user_id: UserId | str, date_: date):
            # user_idがstrの場合はUserIdに変換
            if isinstance(user_id, str):
                user_id = UserId(user_id)
            return self._real_uc.execute(user_id, date_)

    compute_meal_nutrition_use_case = FakeComputeMealNutritionUseCase(
        ComputeMealNutritionUseCase(
            meal_entry_query_service=meal_entry_query_service,
            nutrition_uow=nutrition_uow,
            estimator=nutrition_estimator,
            plan_checker=plan_checker,
        )
    )

    compute_daily_nutrition_use_case = FakeComputeDailyNutritionSummaryUseCase(
        ComputeDailyNutritionSummaryUseCase(
            uow=nutrition_uow,
            plan_checker=plan_checker,
        )
    )

    # DIをオーバーライド
    app.dependency_overrides[get_current_user_use_case] = lambda: current_user_use_case
    app.dependency_overrides[get_token_service] = lambda: token_service
    app.dependency_overrides[get_meal_uow] = lambda: meal_uow
    app.dependency_overrides[get_nutrition_uow] = lambda: nutrition_uow
    app.dependency_overrides[get_plan_checker] = lambda: plan_checker
    app.dependency_overrides[
        get_meal_entry_query_service
    ] = lambda: meal_entry_query_service
    app.dependency_overrides[get_nutrition_estimator] = lambda: nutrition_estimator
    app.dependency_overrides[
        get_compute_meal_nutrition_use_case
    ] = lambda: compute_meal_nutrition_use_case
    app.dependency_overrides[
        get_compute_daily_nutrition_summary_use_case
    ] = lambda: compute_daily_nutrition_use_case

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


class TestGetMealAndDailyNutrition:
    """GET /nutrition/meal のテスト"""

    def test_get_meal_and_daily_nutrition_invalid_meal_type(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """異常系: 無効なmeal_typeの場合"""
        _, tokens = authenticated_user

        response = client.get(
            "/api/v1/nutrition/meal?date=2024-01-01&meal_type=invalid&meal_index=1",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_get_meal_and_daily_nutrition_invalid_meal_index_main(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """異常系: mainタイプでmeal_indexがNoneまたは0以下の場合"""
        _, tokens = authenticated_user

        # meal_indexがNoneの場合
        response = client.get(
            "/api/v1/nutrition/meal?date=2024-01-01&meal_type=main",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

        # meal_indexが0の場合
        response = client.get(
            "/api/v1/nutrition/meal?date=2024-01-01&meal_type=main&meal_index=0",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_get_meal_and_daily_nutrition_invalid_meal_index_snack(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """異常系: snackタイプでmeal_indexが指定されている場合"""
        _, tokens = authenticated_user

        response = client.get(
            "/api/v1/nutrition/meal?date=2024-01-01&meal_type=snack&meal_index=1",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_get_meal_and_daily_nutrition_unauthorized(self, client: TestClient):
        """異常系: トークンがない場合"""
        response = client.get(
            "/api/v1/nutrition/meal?date=2024-01-01&meal_type=main&meal_index=1"
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data
