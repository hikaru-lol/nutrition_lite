from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest

from app.application.nutrition.use_cases.compute_meal_nutrition import (
    ComputeMealNutritionUseCase,
)
from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.meal.errors import InvalidMealTypeError, InvalidMealIndexError
from app.domain.meal.value_objects import FoodEntryId, MealType
from app.domain.auth.errors import PremiumFeatureRequiredError
from tests.unit.application.nutrition.fakes import (
    FakeMealEntryQueryService,
    FakeNutritionUnitOfWork,
    FakeNutritionEstimator,
    FakePlanChecker,
    FakeMealNutritionRepository,
)
from tests.fakes.meal_uow import FakeMealUnitOfWork
from tests.unit.application.meal.test_create_food_entry_use_case import (
    FakeFoodEntryRepository,
)

pytestmark = pytest.mark.unit


def _make_user_id() -> UserId:
    return UserId(str(uuid4()))


def _make_food_entry(
    user_id: UserId,
    target_date: date,
    meal_type: MealType,
    meal_index: int | None,
    amount_value: float = 100.0,
) -> FoodEntry:
    """テスト用のFoodEntryを作成"""
    return FoodEntry(
        id=FoodEntryId.new(),
        user_id=user_id,
        date=target_date,
        meal_type=meal_type,
        meal_index=meal_index,
        name="テスト食品",
        amount_value=amount_value,
        amount_unit="g",
        serving_count=None,
        note=None,
    )


def test_compute_meal_nutrition_success_main_meal() -> None:
    """正常系: mainタイプの食事の栄養サマリ計算"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ
    food_entry_repo = FakeFoodEntryRepository()
    meal_uow = FakeMealUnitOfWork(food_entry_repo)
    meal_entry_query = FakeMealEntryQueryService(meal_uow)
    nutrition_uow = FakeNutritionUnitOfWork()
    estimator = FakeNutritionEstimator()
    plan_checker = FakePlanChecker()

    # 食事ログを作成
    entry = _make_food_entry(
        user_id=user_id,
        target_date=target_date,
        meal_type=MealType.MAIN,
        meal_index=1,
        amount_value=150.0,
    )
    food_entry_repo.add(entry)

    # UseCase実行
    use_case = ComputeMealNutritionUseCase(
        meal_entry_query_service=meal_entry_query,
        nutrition_uow=nutrition_uow,
        estimator=estimator,
        plan_checker=plan_checker,
    )

    result = use_case.execute(
        user_id=user_id,
        date_=target_date,
        meal_type_str="main",
        meal_index=1,
    )

    # 検証
    assert result is not None
    assert result.user_id == user_id
    assert result.date == target_date
    assert result.meal_type == MealType.MAIN
    assert result.meal_index == 1
    assert len(result.nutrients) > 0

    # リポジトリに保存されていることを確認
    saved = nutrition_uow.meal_nutrition_repo.get_by_user_date_meal(
        user_id=user_id,
        target_date=target_date,
        meal_type=MealType.MAIN,
        meal_index=1,
    )
    assert saved is not None
    assert saved.id == result.id


def test_compute_meal_nutrition_success_snack() -> None:
    """正常系: snackタイプの食事の栄養サマリ計算"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ
    food_entry_repo = FakeFoodEntryRepository()
    meal_uow = FakeMealUnitOfWork(food_entry_repo)
    meal_entry_query = FakeMealEntryQueryService(meal_uow)
    nutrition_uow = FakeNutritionUnitOfWork()
    estimator = FakeNutritionEstimator()
    plan_checker = FakePlanChecker()

    # 食事ログを作成
    entry = _make_food_entry(
        user_id=user_id,
        target_date=target_date,
        meal_type=MealType.SNACK,
        meal_index=None,
        amount_value=50.0,
    )
    food_entry_repo.add(entry)

    # UseCase実行
    use_case = ComputeMealNutritionUseCase(
        meal_entry_query_service=meal_entry_query,
        nutrition_uow=nutrition_uow,
        estimator=estimator,
        plan_checker=plan_checker,
    )

    result = use_case.execute(
        user_id=user_id,
        date_=target_date,
        meal_type_str="snack",
        meal_index=None,
    )

    # 検証
    assert result is not None
    assert result.meal_type == MealType.SNACK
    assert result.meal_index is None


def test_compute_meal_nutrition_upsert_existing() -> None:
    """正常系: 既存のサマリを更新（upsert）"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ
    food_entry_repo = FakeFoodEntryRepository()
    meal_uow = FakeMealUnitOfWork(food_entry_repo)
    meal_entry_query = FakeMealEntryQueryService(meal_uow)
    meal_nutrition_repo = FakeMealNutritionRepository()
    nutrition_uow = FakeNutritionUnitOfWork(
        meal_nutrition_repo=meal_nutrition_repo)
    estimator = FakeNutritionEstimator()
    plan_checker = FakePlanChecker()

    # 既存のサマリを作成
    from app.domain.nutrition.meal_nutrition import MealNutritionSummary
    from app.domain.target.value_objects import NutrientCode, NutrientAmount, NutrientSource

    existing_summary = MealNutritionSummary.from_nutrient_amounts(
        user_id=user_id,
        date=target_date,
        meal_type=MealType.MAIN,
        meal_index=1,
        nutrients=[
            (NutrientCode.PROTEIN, NutrientAmount(value=10.0, unit="g"))],
        source=NutrientSource("llm"),
        summary_id=None,
    )
    meal_nutrition_repo.save(existing_summary)
    existing_id = existing_summary.id

    # 新しい食事ログを追加
    entry = _make_food_entry(
        user_id=user_id,
        target_date=target_date,
        meal_type=MealType.MAIN,
        meal_index=1,
        amount_value=200.0,
    )
    food_entry_repo.add(entry)

    # UseCase実行
    use_case = ComputeMealNutritionUseCase(
        meal_entry_query_service=meal_entry_query,
        nutrition_uow=nutrition_uow,
        estimator=estimator,
        plan_checker=plan_checker,
    )

    result = use_case.execute(
        user_id=user_id,
        date_=target_date,
        meal_type_str="main",
        meal_index=1,
    )

    # 検証: IDが引き継がれている
    assert result.id == existing_id


def test_compute_meal_nutrition_invalid_meal_type() -> None:
    """異常系: 不正なmeal_type"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ
    food_entry_repo = FakeFoodEntryRepository()
    meal_uow = FakeMealUnitOfWork(food_entry_repo)
    meal_entry_query = FakeMealEntryQueryService(meal_uow)
    nutrition_uow = FakeNutritionUnitOfWork()
    estimator = FakeNutritionEstimator()
    plan_checker = FakePlanChecker()

    use_case = ComputeMealNutritionUseCase(
        meal_entry_query_service=meal_entry_query,
        nutrition_uow=nutrition_uow,
        estimator=estimator,
        plan_checker=plan_checker,
    )

    with pytest.raises(InvalidMealTypeError):
        use_case.execute(
            user_id=user_id,
            date_=target_date,
            meal_type_str="invalid",
            meal_index=1,
        )


def test_compute_meal_nutrition_main_without_index() -> None:
    """異常系: mainタイプでmeal_indexがNone"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ
    food_entry_repo = FakeFoodEntryRepository()
    meal_uow = FakeMealUnitOfWork(food_entry_repo)
    meal_entry_query = FakeMealEntryQueryService(meal_uow)
    nutrition_uow = FakeNutritionUnitOfWork()
    estimator = FakeNutritionEstimator()
    plan_checker = FakePlanChecker()

    use_case = ComputeMealNutritionUseCase(
        meal_entry_query_service=meal_entry_query,
        nutrition_uow=nutrition_uow,
        estimator=estimator,
        plan_checker=plan_checker,
    )

    with pytest.raises(InvalidMealIndexError):
        use_case.execute(
            user_id=user_id,
            date_=target_date,
            meal_type_str="main",
            meal_index=None,
        )


def test_compute_meal_nutrition_main_with_invalid_index() -> None:
    """異常系: mainタイプでmeal_indexが1未満"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ
    food_entry_repo = FakeFoodEntryRepository()
    meal_uow = FakeMealUnitOfWork(food_entry_repo)
    meal_entry_query = FakeMealEntryQueryService(meal_uow)
    nutrition_uow = FakeNutritionUnitOfWork()
    estimator = FakeNutritionEstimator()
    plan_checker = FakePlanChecker()

    use_case = ComputeMealNutritionUseCase(
        meal_entry_query_service=meal_entry_query,
        nutrition_uow=nutrition_uow,
        estimator=estimator,
        plan_checker=plan_checker,
    )

    with pytest.raises(InvalidMealIndexError):
        use_case.execute(
            user_id=user_id,
            date_=target_date,
            meal_type_str="main",
            meal_index=0,
        )


def test_compute_meal_nutrition_snack_with_index() -> None:
    """異常系: snackタイプでmeal_indexが指定されている"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ
    food_entry_repo = FakeFoodEntryRepository()
    meal_uow = FakeMealUnitOfWork(food_entry_repo)
    meal_entry_query = FakeMealEntryQueryService(meal_uow)
    nutrition_uow = FakeNutritionUnitOfWork()
    estimator = FakeNutritionEstimator()
    plan_checker = FakePlanChecker()

    use_case = ComputeMealNutritionUseCase(
        meal_entry_query_service=meal_entry_query,
        nutrition_uow=nutrition_uow,
        estimator=estimator,
        plan_checker=plan_checker,
    )

    with pytest.raises(InvalidMealIndexError):
        use_case.execute(
            user_id=user_id,
            date_=target_date,
            meal_type_str="snack",
            meal_index=1,
        )


def test_compute_meal_nutrition_empty_entries() -> None:
    """正常系: 食事ログが0件でも計算可能（栄養素は0になる）"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ（食事ログなし）
    food_entry_repo = FakeFoodEntryRepository()
    meal_uow = FakeMealUnitOfWork(food_entry_repo)
    meal_entry_query = FakeMealEntryQueryService(meal_uow)
    nutrition_uow = FakeNutritionUnitOfWork()
    estimator = FakeNutritionEstimator()
    plan_checker = FakePlanChecker()

    use_case = ComputeMealNutritionUseCase(
        meal_entry_query_service=meal_entry_query,
        nutrition_uow=nutrition_uow,
        estimator=estimator,
        plan_checker=plan_checker,
    )

    result = use_case.execute(
        user_id=user_id,
        date_=target_date,
        meal_type_str="main",
        meal_index=1,
    )

    # 検証: サマリは作成されるが、栄養素の値は0
    assert result is not None
    assert len(result.nutrients) > 0
    # エントリが0件なので、栄養素の値は0になる
    total_nutrients = sum(n.amount.value for n in result.nutrients)
    assert total_nutrients == 0.0
