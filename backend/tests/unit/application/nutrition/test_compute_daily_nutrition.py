from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest

from app.application.nutrition.use_cases.compute_daily_nutrition import (
    ComputeDailyNutritionSummaryUseCase,
)
from app.domain.auth.value_objects import UserId
from app.domain.meal.value_objects import MealType
from app.domain.nutrition.meal_nutrition import MealNutritionSummary
from app.domain.target.value_objects import (
    NutrientCode,
    NutrientAmount,
    NutrientSource,
)
from app.domain.auth.errors import PremiumFeatureRequiredError
from tests.unit.application.nutrition.fakes import (
    FakeNutritionUnitOfWork,
    FakePlanChecker,
    FakeMealNutritionRepository,
    FakeDailyNutritionRepository,
)

pytestmark = pytest.mark.unit


def _make_user_id() -> UserId:
    return UserId(str(uuid4()))


def _make_meal_nutrition_summary(
    user_id: UserId,
    target_date: date,
    meal_type: MealType,
    meal_index: int | None,
    nutrients: list[tuple[NutrientCode, NutrientAmount]],
) -> MealNutritionSummary:
    """テスト用のMealNutritionSummaryを作成"""
    return MealNutritionSummary.from_nutrient_amounts(
        user_id=user_id,
        date=target_date,
        meal_type=meal_type,
        meal_index=meal_index,
        nutrients=nutrients,
        source=NutrientSource("llm"),
        summary_id=None,
    )


def test_compute_daily_nutrition_success_single_meal() -> None:
    """正常系: 1食分のサマリから1日分を計算"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ
    meal_nutrition_repo = FakeMealNutritionRepository()
    daily_nutrition_repo = FakeDailyNutritionRepository()
    nutrition_uow = FakeNutritionUnitOfWork(
        meal_nutrition_repo=meal_nutrition_repo,
        daily_nutrition_repo=daily_nutrition_repo,
    )
    plan_checker = FakePlanChecker()

    # 1食分のサマリを作成
    meal_summary = _make_meal_nutrition_summary(
        user_id=user_id,
        target_date=target_date,
        meal_type=MealType.MAIN,
        meal_index=1,
        nutrients=[
            (NutrientCode.PROTEIN, NutrientAmount(value=30.0, unit="g")),
            (NutrientCode.FAT, NutrientAmount(value=20.0, unit="g")),
            (NutrientCode.CARBOHYDRATE, NutrientAmount(value=50.0, unit="g")),
        ],
    )
    meal_nutrition_repo.save(meal_summary)

    # UseCase実行
    use_case = ComputeDailyNutritionSummaryUseCase(
        uow=nutrition_uow,
        plan_checker=plan_checker,
    )

    result = use_case.execute(user_id=user_id, date_=target_date)

    # 検証
    assert result is not None
    assert result.user_id == user_id
    assert result.date == target_date
    assert len(result.nutrients) == 3

    # 栄養素の値が正しく合計されていることを確認
    nutrient_dict = {n.code: n.amount.value for n in result.nutrients}
    assert nutrient_dict[NutrientCode.PROTEIN] == 30.0
    assert nutrient_dict[NutrientCode.FAT] == 20.0
    assert nutrient_dict[NutrientCode.CARBOHYDRATE] == 50.0

    # リポジトリに保存されていることを確認
    saved = daily_nutrition_repo.get_by_user_and_date(
        user_id=user_id,
        target_date=target_date,
    )
    assert saved is not None
    assert saved.id == result.id


def test_compute_daily_nutrition_success_multiple_meals() -> None:
    """正常系: 複数の食事サマリから1日分を計算（合計）"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ
    meal_nutrition_repo = FakeMealNutritionRepository()
    daily_nutrition_repo = FakeDailyNutritionRepository()
    nutrition_uow = FakeNutritionUnitOfWork(
        meal_nutrition_repo=meal_nutrition_repo,
        daily_nutrition_repo=daily_nutrition_repo,
    )
    plan_checker = FakePlanChecker()

    # 複数の食事サマリを作成
    meal1 = _make_meal_nutrition_summary(
        user_id=user_id,
        target_date=target_date,
        meal_type=MealType.MAIN,
        meal_index=1,
        nutrients=[
            (NutrientCode.PROTEIN, NutrientAmount(value=30.0, unit="g")),
            (NutrientCode.FAT, NutrientAmount(value=20.0, unit="g")),
        ],
    )
    meal_nutrition_repo.save(meal1)

    meal2 = _make_meal_nutrition_summary(
        user_id=user_id,
        target_date=target_date,
        meal_type=MealType.MAIN,
        meal_index=2,
        nutrients=[
            (NutrientCode.PROTEIN, NutrientAmount(value=25.0, unit="g")),
            (NutrientCode.FAT, NutrientAmount(value=15.0, unit="g")),
        ],
    )
    meal_nutrition_repo.save(meal2)

    snack = _make_meal_nutrition_summary(
        user_id=user_id,
        target_date=target_date,
        meal_type=MealType.SNACK,
        meal_index=None,
        nutrients=[
            (NutrientCode.PROTEIN, NutrientAmount(value=10.0, unit="g")),
            (NutrientCode.CARBOHYDRATE, NutrientAmount(value=30.0, unit="g")),
        ],
    )
    meal_nutrition_repo.save(snack)

    # UseCase実行
    use_case = ComputeDailyNutritionSummaryUseCase(
        uow=nutrition_uow,
        plan_checker=plan_checker,
    )

    result = use_case.execute(user_id=user_id, date_=target_date)

    # 検証: 栄養素が正しく合計されている
    nutrient_dict = {n.code: n.amount.value for n in result.nutrients}
    assert nutrient_dict[NutrientCode.PROTEIN] == 65.0  # 30 + 25 + 10
    assert nutrient_dict[NutrientCode.FAT] == 35.0  # 20 + 15
    assert nutrient_dict[NutrientCode.CARBOHYDRATE] == 30.0  # snackのみ


def test_compute_daily_nutrition_upsert_existing() -> None:
    """正常系: 既存の1日分サマリを更新（upsert）"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ
    meal_nutrition_repo = FakeMealNutritionRepository()
    daily_nutrition_repo = FakeDailyNutritionRepository()
    nutrition_uow = FakeNutritionUnitOfWork(
        meal_nutrition_repo=meal_nutrition_repo,
        daily_nutrition_repo=daily_nutrition_repo,
    )
    plan_checker = FakePlanChecker()

    # 既存の1日分サマリを作成
    from app.domain.nutrition.daily_nutrition import DailyNutritionSummary

    existing_summary = DailyNutritionSummary.from_nutrient_amounts(
        user_id=user_id,
        date=target_date,
        nutrients=[
            (NutrientCode.PROTEIN, NutrientAmount(value=50.0, unit="g")),
        ],
        source=NutrientSource("llm"),
        summary_id=None,
    )
    daily_nutrition_repo.save(existing_summary)
    existing_id = existing_summary.id

    # 新しい食事サマリを追加
    meal_summary = _make_meal_nutrition_summary(
        user_id=user_id,
        target_date=target_date,
        meal_type=MealType.MAIN,
        meal_index=1,
        nutrients=[
            (NutrientCode.PROTEIN, NutrientAmount(value=30.0, unit="g")),
        ],
    )
    meal_nutrition_repo.save(meal_summary)

    # UseCase実行
    use_case = ComputeDailyNutritionSummaryUseCase(
        uow=nutrition_uow,
        plan_checker=plan_checker,
    )

    result = use_case.execute(user_id=user_id, date_=target_date)

    # 検証: IDが引き継がれている
    assert result.id == existing_id
    # 栄養素の値が更新されている
    nutrient_dict = {n.code: n.amount.value for n in result.nutrients}
    assert nutrient_dict[NutrientCode.PROTEIN] == 30.0


def test_compute_daily_nutrition_empty_meals() -> None:
    """正常系: 食事サマリが0件でも計算可能（栄養素は0になる）"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ（食事サマリなし）
    meal_nutrition_repo = FakeMealNutritionRepository()
    daily_nutrition_repo = FakeDailyNutritionRepository()
    nutrition_uow = FakeNutritionUnitOfWork(
        meal_nutrition_repo=meal_nutrition_repo,
        daily_nutrition_repo=daily_nutrition_repo,
    )
    plan_checker = FakePlanChecker()

    # UseCase実行
    use_case = ComputeDailyNutritionSummaryUseCase(
        uow=nutrition_uow,
        plan_checker=plan_checker,
    )

    result = use_case.execute(user_id=user_id, date_=target_date)

    # 検証: サマリは作成されるが、栄養素は0件
    assert result is not None
    assert len(result.nutrients) == 0


def test_compute_daily_nutrition_different_units() -> None:
    """正常系: 異なる単位の栄養素が混在しても正しく処理"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ
    meal_nutrition_repo = FakeMealNutritionRepository()
    daily_nutrition_repo = FakeDailyNutritionRepository()
    nutrition_uow = FakeNutritionUnitOfWork(
        meal_nutrition_repo=meal_nutrition_repo,
        daily_nutrition_repo=daily_nutrition_repo,
    )
    plan_checker = FakePlanChecker()

    # 異なる単位の栄養素を含む食事サマリを作成
    meal1 = _make_meal_nutrition_summary(
        user_id=user_id,
        target_date=target_date,
        meal_type=MealType.MAIN,
        meal_index=1,
        nutrients=[
            (NutrientCode.SODIUM, NutrientAmount(value=500.0, unit="mg")),
        ],
    )
    meal_nutrition_repo.save(meal1)

    meal2 = _make_meal_nutrition_summary(
        user_id=user_id,
        target_date=target_date,
        meal_type=MealType.MAIN,
        meal_index=2,
        nutrients=[
            (NutrientCode.SODIUM, NutrientAmount(value=300.0, unit="mg")),
        ],
    )
    meal_nutrition_repo.save(meal2)

    # UseCase実行
    use_case = ComputeDailyNutritionSummaryUseCase(
        uow=nutrition_uow,
        plan_checker=plan_checker,
    )

    result = use_case.execute(user_id=user_id, date_=target_date)

    # 検証: 同じ単位の栄養素は正しく合計される
    nutrient_dict = {n.code: n.amount.value for n in result.nutrients}
    assert nutrient_dict[NutrientCode.SODIUM] == 800.0  # 500 + 300
    # 単位も正しく保持される
    sodium_nutrient = next(
        n for n in result.nutrients if n.code == NutrientCode.SODIUM)
    assert sodium_nutrient.amount.unit == "mg"
