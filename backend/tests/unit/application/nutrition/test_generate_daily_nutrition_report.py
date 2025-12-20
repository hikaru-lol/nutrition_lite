from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

from app.application.nutrition.use_cases.generate_daily_nutrition_report import (
    GenerateDailyNutritionReportUseCase,
)
from app.application.meal.dto.daily_log_completion_dto import (
    DailyLogCompletionResultDTO,
)
from app.application.meal.use_cases.check_daily_log_completion import (
    CheckDailyLogCompletionUseCase,
)
from app.application.nutrition.use_cases.compute_daily_nutrition import (
    ComputeDailyNutritionSummaryUseCase,
)
from app.application.target.use_cases.ensure_daily_snapshot import (
    EnsureDailyTargetSnapshotUseCase,
)
from app.application.target.dto.target_dto import EnsureDailySnapshotInputDTO
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.errors import (
    DailyLogNotCompletedError,
    DailyNutritionReportAlreadyExistsError,
)
from app.domain.nutrition.daily_nutrition import DailyNutritionSummary
from app.domain.nutrition.meal_nutrition import MealNutritionSummary
from app.domain.profile.entities import Profile
from app.domain.target.entities import DailyTargetSnapshot
from app.domain.target.value_objects import (
    NutrientCode,
    NutrientAmount,
    NutrientSource,
)
from app.domain.meal.errors import DailyLogProfileNotFoundError
from tests.unit.application.nutrition.fakes import (
    FakeNutritionUnitOfWork,
    FakePlanChecker,
    FakeDailyNutritionReportGenerator,
    FakeDailyNutritionReportRepository,
)
from tests.fakes.auth_services import FixedClock
from tests.fakes.profile_repositories import InMemoryProfileRepository
from tests.fakes.profile_uow import FakeProfileUnitOfWork

pytestmark = pytest.mark.unit


def _make_user_id() -> UserId:
    return UserId(str(uuid4()))


def _make_profile(user_id: UserId, meals_per_day: int = 3) -> Profile:
    """テスト用のProfileを作成"""
    from app.domain.profile.value_objects import Sex, HeightCm, WeightKg, ProfileImageId

    return Profile(
        user_id=user_id,
        sex=Sex.MALE,
        birthdate=date(1990, 1, 1),
        height_cm=HeightCm(175.0),
        weight_kg=WeightKg(70.0),
        image_id=ProfileImageId("test-image-id"),
        meals_per_day=meals_per_day,
    )


def _make_daily_nutrition_summary(
    user_id: UserId, target_date: date
) -> DailyNutritionSummary:
    """テスト用のDailyNutritionSummaryを作成"""
    return DailyNutritionSummary.from_nutrient_amounts(
        user_id=user_id,
        date=target_date,
        nutrients=[
            (NutrientCode.PROTEIN, NutrientAmount(value=100.0, unit="g")),
            (NutrientCode.FAT, NutrientAmount(value=50.0, unit="g")),
        ],
        source=NutrientSource("llm"),
        summary_id=None,
    )


def _make_daily_target_snapshot(user_id: UserId, target_date: date) -> DailyTargetSnapshot:
    """テスト用のDailyTargetSnapshotを作成"""
    from app.domain.target.value_objects import (
        GoalType,
        ActivityLevel,
        NutrientCode,
        NutrientAmount,
        NutrientSource,
        TargetId,
    )
    from app.domain.target.entities import TargetDefinition, TargetNutrient
    from datetime import datetime, timezone
    from uuid import uuid4

    # 簡易的なTargetDefinitionを作成
    target = TargetDefinition(
        id=TargetId(str(uuid4())),
        user_id=user_id,
        title="テストターゲット",
        goal_type=GoalType.WEIGHT_LOSS,
        goal_description=None,
        activity_level=ActivityLevel.NORMAL,
        nutrients=[
            TargetNutrient(
                code=NutrientCode.PROTEIN,
                amount=NutrientAmount(value=100.0, unit="g"),
                source=NutrientSource("llm"),
            ),
        ],
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    return DailyTargetSnapshot.from_target(
        target=target,
        snapshot_date=target_date,
    )


class FakeCheckDailyLogCompletionUseCase(CheckDailyLogCompletionUseCase):
    """Fake実装: 常に完了状態を返す"""

    def __init__(self, is_completed: bool = True) -> None:
        self._is_completed = is_completed
        # 親クラスの初期化をスキップ
        super().__init__(
            profile_query=None,  # type: ignore
            meal_uow=None,  # type: ignore
        )

    def execute(
        self,
        user_id: UserId,
        date_: date,
    ) -> DailyLogCompletionResultDTO:
        if self._is_completed:
            return DailyLogCompletionResultDTO(
                user_id=user_id,
                date=date_,
                meals_per_day=3,
                is_completed=True,
                filled_indices=[1, 2, 3],
                missing_indices=[],
            )
        else:
            return DailyLogCompletionResultDTO(
                user_id=user_id,
                date=date_,
                meals_per_day=3,
                is_completed=False,
                filled_indices=[1],
                missing_indices=[2, 3],
            )


class FakeProfileQueryPort:
    """Fake実装: ProfileQueryPort"""

    def __init__(self, profile: Profile | None = None) -> None:
        self._profile = profile

    def get_profile_for_daily_log(self, user_id: UserId) -> Profile | None:
        return self._profile

    def get_profile_for_target(self, user_id: UserId):
        return None  # type: ignore

    def get_profile_for_recommendation(self, user_id: UserId):
        return None  # type: ignore


class FakeEnsureDailyTargetSnapshotUseCase:
    """Fake実装: 固定のDailyTargetSnapshotを返す"""

    def __init__(self, snapshot: DailyTargetSnapshot | None = None) -> None:
        self._snapshot = snapshot

    def execute(
        self,
        user_id: UserId,
        date_: date,
    ) -> DailyTargetSnapshot:
        if self._snapshot is None:
            return _make_daily_target_snapshot(user_id, date_)
        return self._snapshot


class FakeComputeDailyNutritionSummaryUseCase(ComputeDailyNutritionSummaryUseCase):
    """Fake実装: 固定のDailyNutritionSummaryを返す"""

    def __init__(self, summary: DailyNutritionSummary | None = None) -> None:
        self._summary = summary
        super().__init__(uow=None, plan_checker=None)  # type: ignore

    def execute(self, user_id: UserId, date_: date) -> DailyNutritionSummary:
        if self._summary is None:
            return _make_daily_nutrition_summary(user_id, date_)
        return self._summary


def test_generate_daily_nutrition_report_success() -> None:
    """正常系: 日次レポート生成成功"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ
    profile = _make_profile(user_id, meals_per_day=3)
    profile_query = FakeProfileQueryPort(profile=profile)
    daily_log_uc = FakeCheckDailyLogCompletionUseCase(is_completed=True)
    snapshot = _make_daily_target_snapshot(user_id, target_date)
    ensure_snapshot_uc = FakeEnsureDailyTargetSnapshotUseCase(
        snapshot=snapshot)
    daily_summary = _make_daily_nutrition_summary(user_id, target_date)
    daily_nutrition_uc = FakeComputeDailyNutritionSummaryUseCase(
        summary=daily_summary
    )
    daily_report_repo = FakeDailyNutritionReportRepository()
    nutrition_uow = FakeNutritionUnitOfWork(
        daily_report_repo=daily_report_repo)
    report_generator = FakeDailyNutritionReportGenerator()
    clock = FixedClock()
    plan_checker = FakePlanChecker()

    # UseCase実行
    use_case = GenerateDailyNutritionReportUseCase(
        daily_log_uc=daily_log_uc,
        profile_query=profile_query,
        ensure_target_snapshot_uc=ensure_snapshot_uc,
        daily_nutrition_uc=daily_nutrition_uc,
        nutrition_uow=nutrition_uow,
        report_generator=report_generator,
        clock=clock,
        plan_checker=plan_checker,
    )

    result = use_case.execute(user_id=user_id, date_=target_date)

    # 検証
    assert result is not None
    assert result.user_id == user_id
    assert result.date == target_date
    assert result.summary is not None
    assert len(result.good_points) > 0
    assert len(result.improvement_points) > 0
    assert len(result.tomorrow_focus) > 0

    # リポジトリに保存されていることを確認
    saved = daily_report_repo.get_by_user_and_date(
        user_id=user_id,
        target_date=target_date,
    )
    assert saved is not None
    assert saved.id == result.id


def test_generate_daily_nutrition_report_daily_log_not_completed() -> None:
    """異常系: 食事ログが完了していない"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ
    profile = _make_profile(user_id, meals_per_day=3)
    profile_query = FakeProfileQueryPort(profile=profile)
    daily_log_uc = FakeCheckDailyLogCompletionUseCase(is_completed=False)
    snapshot = _make_daily_target_snapshot(user_id, target_date)
    ensure_snapshot_uc = FakeEnsureDailyTargetSnapshotUseCase(
        snapshot=snapshot)
    daily_summary = _make_daily_nutrition_summary(user_id, target_date)
    daily_nutrition_uc = FakeComputeDailyNutritionSummaryUseCase(
        summary=daily_summary
    )
    nutrition_uow = FakeNutritionUnitOfWork()
    report_generator = FakeDailyNutritionReportGenerator()
    clock = FixedClock()
    plan_checker = FakePlanChecker()

    use_case = GenerateDailyNutritionReportUseCase(
        daily_log_uc=daily_log_uc,
        profile_query=profile_query,
        ensure_target_snapshot_uc=ensure_snapshot_uc,
        daily_nutrition_uc=daily_nutrition_uc,
        nutrition_uow=nutrition_uow,
        report_generator=report_generator,
        clock=clock,
        plan_checker=plan_checker,
    )

    with pytest.raises(DailyLogNotCompletedError):
        use_case.execute(user_id=user_id, date_=target_date)


def test_generate_daily_nutrition_report_already_exists() -> None:
    """異常系: 既にレポートが存在する"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ
    profile = _make_profile(user_id, meals_per_day=3)
    profile_query = FakeProfileQueryPort(profile=profile)
    daily_log_uc = FakeCheckDailyLogCompletionUseCase(is_completed=True)
    snapshot = _make_daily_target_snapshot(user_id, target_date)
    ensure_snapshot_uc = FakeEnsureDailyTargetSnapshotUseCase(
        snapshot=snapshot)
    daily_summary = _make_daily_nutrition_summary(user_id, target_date)
    daily_nutrition_uc = FakeComputeDailyNutritionSummaryUseCase(
        summary=daily_summary
    )
    daily_report_repo = FakeDailyNutritionReportRepository()

    # 既存のレポートを作成
    from app.domain.nutrition.daily_report import DailyNutritionReport

    existing_report = DailyNutritionReport.create(
        user_id=user_id,
        date=target_date,
        summary="既存のレポート",
        good_points=[],
        improvement_points=[],
        tomorrow_focus=[],
        created_at=datetime.now(timezone.utc),
    )
    daily_report_repo.save(existing_report)

    nutrition_uow = FakeNutritionUnitOfWork(
        daily_report_repo=daily_report_repo)
    report_generator = FakeDailyNutritionReportGenerator()
    clock = FixedClock()
    plan_checker = FakePlanChecker()

    use_case = GenerateDailyNutritionReportUseCase(
        daily_log_uc=daily_log_uc,
        profile_query=profile_query,
        ensure_target_snapshot_uc=ensure_snapshot_uc,
        daily_nutrition_uc=daily_nutrition_uc,
        nutrition_uow=nutrition_uow,
        report_generator=report_generator,
        clock=clock,
        plan_checker=plan_checker,
    )

    with pytest.raises(DailyNutritionReportAlreadyExistsError):
        use_case.execute(user_id=user_id, date_=target_date)


def test_generate_daily_nutrition_report_profile_not_found() -> None:
    """異常系: Profileが存在しない"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ（Profileなし）
    profile_query = FakeProfileQueryPort(profile=None)
    daily_log_uc = FakeCheckDailyLogCompletionUseCase(is_completed=True)
    snapshot = _make_daily_target_snapshot(user_id, target_date)
    ensure_snapshot_uc = FakeEnsureDailyTargetSnapshotUseCase(
        snapshot=snapshot)
    daily_summary = _make_daily_nutrition_summary(user_id, target_date)
    daily_nutrition_uc = FakeComputeDailyNutritionSummaryUseCase(
        summary=daily_summary
    )
    nutrition_uow = FakeNutritionUnitOfWork()
    report_generator = FakeDailyNutritionReportGenerator()
    clock = FixedClock()
    plan_checker = FakePlanChecker()

    use_case = GenerateDailyNutritionReportUseCase(
        daily_log_uc=daily_log_uc,
        profile_query=profile_query,
        ensure_target_snapshot_uc=ensure_snapshot_uc,
        daily_nutrition_uc=daily_nutrition_uc,
        nutrition_uow=nutrition_uow,
        report_generator=report_generator,
        clock=clock,
        plan_checker=plan_checker,
    )

    with pytest.raises(DailyLogProfileNotFoundError):
        use_case.execute(user_id=user_id, date_=target_date)
