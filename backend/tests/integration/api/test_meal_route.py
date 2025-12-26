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
    get_create_food_entry_use_case,
    get_current_user_use_case,
    get_delete_food_entry_use_case,
    get_list_food_entries_by_date_use_case,
    get_meal_uow,
    get_nutrition_uow,
    get_plan_checker,
    get_token_service,
    get_update_food_entry_use_case,
)
from app.main import create_app
from app.application.auth.use_cases.current_user.get_current_user import (
    GetCurrentUserUseCase,
)
from app.application.meal.use_cases.create_food_entry import CreateFoodEntryUseCase
from app.application.meal.use_cases.delete_food_entry import DeleteFoodEntryUseCase
from app.application.meal.use_cases.list_food_entries_by_date import (
    ListFoodEntriesByDateUseCase,
)
from app.application.meal.use_cases.update_food_entry import UpdateFoodEntryUseCase
from app.application.nutrition.use_cases.compute_daily_nutrition import (
    ComputeDailyNutritionSummaryUseCase,
)
from app.application.meal.ports.food_entry_repository_port import (
    FoodEntryRepositoryPort,
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
from app.domain.meal.value_objects import FoodEntryId, MealType
from app.domain.nutrition.meal_nutrition import MealNutritionSummary
from app.domain.nutrition.daily_nutrition import DailyNutritionSummary
from tests.fakes.auth_repositories import InMemoryUserRepository
from tests.fakes.auth_services import FakePasswordHasher, FakeTokenService, FixedClock
from tests.fakes.auth_uow import FakeAuthUnitOfWork
from tests.fakes.meal_uow import FakeMealUnitOfWork

# テスト用の固定UUID
TEST_USER_ID = uuid.UUID("12345678-1234-5678-1234-567812345678")


# =====================================================================
# Fake Repositories for Nutrition
# =====================================================================


class FakeMealNutritionRepository(MealNutritionSummaryRepositoryPort):
    """インメモリのMealNutritionSummaryRepository"""

    def __init__(self) -> None:
        self._summaries: list[MealNutritionSummary] = []

    def get_by_user_date_meal(
        self,
        *,
        user_id: UserId,
        target_date: date,
        meal_type: MealType,
        meal_index: int | None,
    ) -> MealNutritionSummary | None:
        user_id_value = getattr(user_id, "value", str(user_id))
        for s in self._summaries:
            if (
                getattr(s.user_id, "value", str(s.user_id)) == user_id_value
                and s.date == target_date
                and s.meal_type == meal_type
                and s.meal_index == meal_index
            ):
                return s
        return None

    def list_by_user_and_date(
        self,
        *,
        user_id: UserId,
        target_date: date,
    ) -> Sequence[MealNutritionSummary]:
        user_id_value = getattr(user_id, "value", str(user_id))
        return [
            s
            for s in self._summaries
            if getattr(s.user_id, "value", str(s.user_id)) == user_id_value
            and s.date == target_date
        ]

    def save(self, summary: MealNutritionSummary) -> None:
        # 既存のものを削除して追加（upsert）
        self._summaries = [
            s
            for s in self._summaries
            if not (
                s.user_id == summary.user_id
                and s.date == summary.date
                and s.meal_type == summary.meal_type
                and s.meal_index == summary.meal_index
            )
        ]
        self._summaries.append(summary)


class FakeDailyNutritionRepository(DailyNutritionSummaryRepositoryPort):
    """インメモリのDailyNutritionSummaryRepository"""

    def __init__(self) -> None:
        self._summaries: dict[str, DailyNutritionSummary] = {}

    def get_by_user_and_date(
        self,
        *,
        user_id: UserId,
        target_date: date,
    ) -> DailyNutritionSummary | None:
        user_id_value = getattr(user_id, "value", str(user_id))
        key = f"{user_id_value}:{target_date}"
        return self._summaries.get(key)

    def save(self, summary: DailyNutritionSummary) -> None:
        user_id_value = getattr(summary.user_id, "value", str(summary.user_id))
        key = f"{user_id_value}:{summary.date}"
        self._summaries[key] = summary


class FakeNutritionUnitOfWork(DailyNutritionUnitOfWorkPort):
    """インメモリのNutritionUnitOfWork"""

    def __init__(
        self,
        meal_nutrition_repo: MealNutritionSummaryRepositoryPort | None = None,
        daily_nutrition_repo: DailyNutritionSummaryRepositoryPort | None = None,
    ) -> None:
        self.meal_nutrition_repo = (
            meal_nutrition_repo or FakeMealNutritionRepository()
        )
        self.daily_nutrition_repo = (
            daily_nutrition_repo or FakeDailyNutritionRepository()
        )
        self._committed = False

    def __enter__(self) -> "FakeNutritionUnitOfWork":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    def commit(self) -> None:
        self._committed = True

    def rollback(self) -> None:
        self._committed = False


class FakeFoodEntryRepository(FoodEntryRepositoryPort):
    """メモリ上にFoodEntryを保持するFake実装"""

    def __init__(self) -> None:
        self.entries: dict[str, FoodEntry] = {}

    def add(self, entry: FoodEntry) -> None:
        self.entries[str(entry.id.value)] = entry

    def update(self, entry: FoodEntry) -> None:
        self.entries[str(entry.id.value)] = entry

    def delete(self, entry: FoodEntry) -> None:
        # ソフトデリート: deleted_atを設定
        stored = self.entries.get(str(entry.id.value))
        if stored:
            from datetime import datetime, timezone

            stored.deleted_at = datetime.now(timezone.utc)

    def get_by_id(
        self, user_id: UserId, entry_id: FoodEntryId
    ) -> FoodEntry | None:
        entry = self.entries.get(str(entry_id.value))
        if entry:
            # UserIdの比較: value属性を比較
            entry_user_id_value = getattr(
                entry.user_id, "value", str(entry.user_id))
            user_id_value = getattr(user_id, "value", str(user_id))
            if entry_user_id_value == user_id_value:
                return entry
        return None

    def list_by_user_and_date(
        self, user_id: UserId, target_date: date
    ) -> Sequence[FoodEntry]:
        user_id_value = getattr(user_id, "value", str(user_id))
        return [
            e
            for e in self.entries.values()
            if getattr(e.user_id, "value", str(e.user_id)) == user_id_value
            and e.date == target_date
            and e.deleted_at is None
        ]

    def list_by_user_date_type_index(
        self,
        user_id: UserId,
        target_date: date,
        meal_type: MealType,
        meal_index: int | None,
    ) -> Sequence[FoodEntry]:
        user_id_value = getattr(user_id, "value", str(user_id))
        return [
            e
            for e in self.entries.values()
            if getattr(e.user_id, "value", str(e.user_id)) == user_id_value
            and e.date == target_date
            and e.meal_type == meal_type
            and e.meal_index == meal_index
            and e.deleted_at is None
        ]

    def clear(self) -> None:
        self.entries.clear()


class FakePlanChecker(PlanCheckerPort):
    """常にプレミアム機能を許可するFake実装"""

    def ensure_premium_feature(self, user_id: UserId) -> None:
        # テストでは常に許可
        pass


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
def app(
    user_repo: InMemoryUserRepository,
    password_hasher: FakePasswordHasher,
    token_service: FakeTokenService,
    clock: FixedClock,
    auth_uow: FakeAuthUnitOfWork,
    meal_uow: FakeMealUnitOfWork,
    nutrition_uow: FakeNutritionUnitOfWork,
    plan_checker: FakePlanChecker,
) -> FastAPI:
    """
    FAKEを使ったDIオーバーライドでFastAPIアプリを作成
    """
    app = create_app()

    # UseCaseをFAKEで作成
    current_user_use_case = GetCurrentUserUseCase(
        uow=auth_uow,
    )

    # UseCaseをラップしてuser_idをUserIdに変換
    class FakeCreateFoodEntryUseCase:
        def __init__(self, real_uc: CreateFoodEntryUseCase) -> None:
            self._real_uc = real_uc

        def execute(self, user_id: UserId | str, dto) -> FoodEntryDTO:
            if isinstance(user_id, str):
                user_id = UserId(user_id)
            return self._real_uc.execute(user_id, dto)

    class FakeListFoodEntriesUseCase:
        def __init__(self, real_uc: ListFoodEntriesByDateUseCase) -> None:
            self._real_uc = real_uc

        def execute(self, user_id: UserId | str, target_date: date) -> Sequence[FoodEntryDTO]:
            if isinstance(user_id, str):
                user_id = UserId(user_id)
            return self._real_uc.execute(user_id, target_date)

    class FakeUpdateFoodEntryUseCase:
        def __init__(self, real_uc: UpdateFoodEntryUseCase) -> None:
            self._real_uc = real_uc

        def execute(self, user_id: UserId | str, dto) -> UpdateFoodEntryResultDTO:
            if isinstance(user_id, str):
                user_id = UserId(user_id)
            return self._real_uc.execute(user_id, dto)

    class FakeDeleteFoodEntryUseCase:
        def __init__(self, real_uc: DeleteFoodEntryUseCase) -> None:
            self._real_uc = real_uc

        def execute(self, user_id: UserId | str, entry_id_str: str) -> DeleteFoodEntryResultDTO:
            if isinstance(user_id, str):
                user_id = UserId(user_id)
            return self._real_uc.execute(user_id, entry_id_str)

    create_food_entry_use_case = FakeCreateFoodEntryUseCase(
        CreateFoodEntryUseCase(meal_uow=meal_uow)
    )

    list_food_entries_use_case = FakeListFoodEntriesUseCase(
        ListFoodEntriesByDateUseCase(meal_uow=meal_uow)
    )

    update_food_entry_use_case = FakeUpdateFoodEntryUseCase(
        UpdateFoodEntryUseCase(meal_uow=meal_uow)
    )

    delete_food_entry_use_case = FakeDeleteFoodEntryUseCase(
        DeleteFoodEntryUseCase(meal_uow=meal_uow)
    )

    # ComputeDailyNutritionSummaryUseCaseをラップしてuser_idをUserIdに変換
    class FakeComputeDailyNutritionSummaryUseCase:
        def __init__(self, real_uc: ComputeDailyNutritionSummaryUseCase) -> None:
            self._real_uc = real_uc

        def execute(self, user_id: UserId | str, date_: DateType) -> DailyNutritionSummary:
            # user_idがstrの場合はUserIdに変換
            if isinstance(user_id, str):
                user_id = UserId(user_id)
            return self._real_uc.execute(user_id, date_)

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
        get_create_food_entry_use_case
    ] = lambda: create_food_entry_use_case
    app.dependency_overrides[
        get_list_food_entries_by_date_use_case
    ] = lambda: list_food_entries_use_case
    app.dependency_overrides[
        get_update_food_entry_use_case
    ] = lambda: update_food_entry_use_case
    app.dependency_overrides[
        get_delete_food_entry_use_case
    ] = lambda: delete_food_entry_use_case
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


class TestCreateMealItem:
    """POST /meal-items のテスト"""

    def test_create_meal_item_success(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """正常系: 食事ログ作成が成功する"""
        _, tokens = authenticated_user

        response = client.post(
            "/api/v1/meal-items",
            json={
                "date": "2024-01-01",
                "meal_type": "main",
                "meal_index": 1,
                "name": "Rice Bowl",
                "amount_value": 200.0,
                "amount_unit": "g",
                "serving_count": None,
                "note": "Lunch",
            },
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Rice Bowl"
        assert data["meal_type"] == "main"
        assert data["meal_index"] == 1
        assert data["amount_value"] == 200.0
        assert data["amount_unit"] == "g"

    def test_create_meal_item_with_serving_count(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """正常系: serving_countで作成"""
        _, tokens = authenticated_user

        response = client.post(
            "/api/v1/meal-items",
            json={
                "date": "2024-01-01",
                "meal_type": "main",
                "meal_index": 1,
                "name": "Curry",
                "amount_value": None,
                "amount_unit": None,
                "serving_count": 1.5,
                "note": None,
            },
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Curry"
        assert data["serving_count"] == 1.5

    def test_create_meal_item_snack(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """正常系: snackタイプで作成"""
        _, tokens = authenticated_user

        response = client.post(
            "/api/v1/meal-items",
            json={
                "date": "2024-01-01",
                "meal_type": "snack",
                "meal_index": None,
                "name": "Apple",
                "amount_value": 150.0,
                "amount_unit": "g",
                "serving_count": None,
                "note": None,
            },
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["meal_type"] == "snack"
        assert data["meal_index"] is None

    def test_create_meal_item_unauthorized(self, client: TestClient):
        """異常系: トークンがない場合"""
        response = client.post(
            "/api/v1/meal-items",
            json={
                "date": "2024-01-01",
                "meal_type": "main",
                "meal_index": 1,
                "name": "Rice Bowl",
                "amount_value": 200.0,
                "amount_unit": "g",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestListMealItems:
    """GET /meal-items のテスト"""

    def test_list_meal_items_success(
        self,
        client: TestClient,
        meal_uow: FakeMealUnitOfWork,
        authenticated_user: tuple[User, TokenPair],
        clock: FixedClock,
    ):
        """正常系: 指定日の食事ログ一覧取得が成功する"""
        user, tokens = authenticated_user

        # 食事ログを作成（meal_uowのfood_entry_repoに直接追加）
        from app.domain.meal.entities import FoodEntry
        from app.domain.meal.value_objects import FoodEntryId, MealType

        entry1 = FoodEntry(
            id=FoodEntryId.new(),
            user_id=user.id,
            date=date(2024, 1, 1),
            meal_type=MealType.MAIN,
            meal_index=1,
            name="Breakfast",
            amount_value=300.0,
            amount_unit="g",
            serving_count=None,
            note=None,
            created_at=clock.now(),
            updated_at=clock.now(),
            deleted_at=None,
        )
        entry2 = FoodEntry(
            id=FoodEntryId.new(),
            user_id=user.id,
            date=date(2024, 1, 1),
            meal_type=MealType.SNACK,
            meal_index=None,
            name="Apple",
            amount_value=150.0,
            amount_unit="g",
            serving_count=None,
            note=None,
            created_at=clock.now(),
            updated_at=clock.now(),
            deleted_at=None,
        )
        meal_uow.food_entry_repo.add(entry1)
        meal_uow.food_entry_repo.add(entry2)

        response = client.get(
            "/api/v1/meal-items?date=2024-01-01",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 2

    def test_list_meal_items_empty(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """正常系: 食事ログが0件の場合"""
        _, tokens = authenticated_user

        response = client.get(
            "/api/v1/meal-items?date=2024-01-01",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 0

    def test_list_meal_items_unauthorized(self, client: TestClient):
        """異常系: トークンがない場合"""
        response = client.get("/api/v1/meal-items?date=2024-01-01")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestUpdateMealItem:
    """PATCH /meal-items/{entry_id} のテスト"""

    def test_update_meal_item_success(
        self,
        client: TestClient,
        meal_uow: FakeMealUnitOfWork,
        authenticated_user: tuple[User, TokenPair],
        clock: FixedClock,
    ):
        """正常系: 食事ログ更新が成功する"""
        user, tokens = authenticated_user

        # 食事ログを作成（meal_uowのfood_entry_repoに直接追加）
        from app.domain.meal.entities import FoodEntry
        from app.domain.meal.value_objects import FoodEntryId, MealType

        entry = FoodEntry(
            id=FoodEntryId.new(),
            user_id=user.id,
            date=date(2024, 1, 1),
            meal_type=MealType.MAIN,
            meal_index=1,
            name="Original Name",
            amount_value=200.0,
            amount_unit="g",
            serving_count=None,
            note=None,
            created_at=clock.now(),
            updated_at=clock.now(),
            deleted_at=None,
        )
        meal_uow.food_entry_repo.add(entry)
        entry_id = str(entry.id.value)

        response = client.patch(
            f"/api/v1/meal-items/{entry_id}",
            json={
                "date": "2024-01-01",
                "meal_type": "main",
                "meal_index": 1,
                "name": "Updated Name",
                "amount_value": 250.0,
                "amount_unit": "g",
                "serving_count": None,
                "note": "Updated note",
            },
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["amount_value"] == 250.0
        assert data["note"] == "Updated note"

    def test_update_meal_item_not_found(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """異常系: 食事ログが存在しない場合"""
        _, tokens = authenticated_user

        # 有効なUUID形式で存在しないIDを使用
        fake_id = str(uuid.uuid4())
        response = client.patch(
            f"/api/v1/meal-items/{fake_id}",
            json={
                "date": "2024-01-01",
                "meal_type": "main",
                "meal_index": 1,
                "name": "Updated Name",
                "amount_value": 250.0,
                "amount_unit": "g",
            },
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_update_meal_item_unauthorized(self, client: TestClient):
        """異常系: トークンがない場合"""
        response = client.patch(
            "/api/v1/meal-items/some-id",
            json={
                "date": "2024-01-01",
                "meal_type": "main",
                "meal_index": 1,
                "name": "Updated Name",
                "amount_value": 250.0,
                "amount_unit": "g",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data


class TestDeleteMealItem:
    """DELETE /meal-items/{entry_id} のテスト"""

    def test_delete_meal_item_success(
        self,
        client: TestClient,
        meal_uow: FakeMealUnitOfWork,
        authenticated_user: tuple[User, TokenPair],
        clock: FixedClock,
    ):
        """正常系: 食事ログ削除が成功する"""
        user, tokens = authenticated_user

        # 食事ログを作成（meal_uowのfood_entry_repoに直接追加）
        from app.domain.meal.entities import FoodEntry
        from app.domain.meal.value_objects import FoodEntryId, MealType

        entry = FoodEntry(
            id=FoodEntryId.new(),
            user_id=user.id,
            date=date(2024, 1, 1),
            meal_type=MealType.MAIN,
            meal_index=1,
            name="To Delete",
            amount_value=200.0,
            amount_unit="g",
            serving_count=None,
            note=None,
            created_at=clock.now(),
            updated_at=clock.now(),
            deleted_at=None,
        )
        meal_uow.food_entry_repo.add(entry)
        entry_id = str(entry.id.value)

        response = client.delete(
            f"/api/v1/meal-items/{entry_id}",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 204

        # ソフトデリートされていることを確認
        deleted_entry = meal_uow.food_entry_repo.get_by_id(
            user.id, FoodEntryId(uuid.UUID(entry_id))
        )
        assert deleted_entry is not None
        assert deleted_entry.deleted_at is not None

    def test_delete_meal_item_not_found(
        self,
        client: TestClient,
        authenticated_user: tuple[User, TokenPair],
    ):
        """異常系: 食事ログが存在しない場合"""
        _, tokens = authenticated_user

        # 有効なUUID形式で存在しないIDを使用
        fake_id = str(uuid.uuid4())
        response = client.delete(
            f"/api/v1/meal-items/{fake_id}",
            cookies={
                "ACCESS_TOKEN": tokens.access_token,
            },
        )

        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_delete_meal_item_unauthorized(self, client: TestClient):
        """異常系: トークンがない場合"""
        response = client.delete("/api/v1/meal-items/some-id")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data
