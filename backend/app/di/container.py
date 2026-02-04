from __future__ import annotations

# === Standard library =======================================================
import os
from typing import Callable, TypeVar, cast

# === Third-party ============================================================
from fastapi import Depends
from fastapi.params import Depends as DependsParam
from sqlalchemy.orm import Session

# === Core settings / infra ==================================================
from app.settings import settings
from app.infra.db.session import create_session
from app.infra.time.system_clock import SystemClock

# === Auth ===================================================================
# Ports
from app.application.auth.ports.clock_port import ClockPort
from app.application.auth.ports.password_hasher_port import PasswordHasherPort
from app.application.auth.ports.token_service_port import TokenServicePort
from app.application.auth.ports.uow_port import AuthUnitOfWorkPort

# Use cases
from app.application.auth.use_cases.account.delete_account import DeleteAccountUseCase
from app.application.auth.use_cases.account.register_user import RegisterUserUseCase
from app.application.auth.use_cases.current_user.get_current_user import (
    GetCurrentUserUseCase,
)
from app.application.auth.use_cases.session.login_user import LoginUserUseCase
from app.application.auth.use_cases.session.logout_user import LogoutUserUseCase
from app.application.auth.use_cases.session.refresh_token import RefreshTokenUseCase

# Infra (repo / security / uow)
from app.infra.db.uow.auth import SqlAlchemyAuthUnitOfWork
from app.infra.security.jwt_token_service import JwtTokenService
from app.infra.security.password_hasher import BcryptPasswordHasher

# === Auth: PlanChecker ======================================================
# Ports
from app.application.auth.ports.plan_checker_port import PlanCheckerPort
# Infra
from app.infra.auth.plan_checker_service import PlanCheckerService

# === Profile ================================================================
# Ports
from app.application.profile.ports.profile_image_storage_port import (
    ProfileImageStoragePort,
)
from app.application.profile.ports.uow_port import ProfileUnitOfWorkPort
from app.application.profile.ports.profile_query_port import ProfileQueryPort

# Use cases
from app.application.profile.use_cases.get_my_profile import GetMyProfileUseCase
from app.application.profile.use_cases.upsert_profile import UpsertProfileUseCase

# Infra (repo / uow / storage / query service)
from app.infra.db.uow.profile import SqlAlchemyProfileUnitOfWork
from app.infra.profile.profile_query_service import ProfileQueryService
from app.infra.storage.minio_profile_image_storage import MinioProfileImageStorage
from app.infra.storage.profile_image_storage import InMemoryProfileImageStorage

# === Target ================================================================
# Ports
from app.application.target.ports.target_generator_port import TargetGeneratorPort
from app.application.target.ports.uow_port import TargetUnitOfWorkPort

# Use cases
from app.application.target.use_cases.activate_target import ActivateTargetUseCase
from app.application.target.use_cases.create_target import CreateTargetUseCase
from app.application.target.use_cases.ensure_daily_snapshot import (
    EnsureDailyTargetSnapshotUseCase,
)
from app.application.target.use_cases.get_active_target import GetActiveTargetUseCase
from app.application.target.use_cases.get_target import GetTargetUseCase
from app.application.target.use_cases.list_targets import ListTargetsUseCase
from app.application.target.use_cases.update_target import UpdateTargetUseCase
from app.application.target.use_cases.delete_target import DeleteTargetUseCase

# Infra (repo / uow / llm)
from app.infra.db.uow.target import SqlAlchemyTargetUnitOfWork
from app.infra.llm.target_generator_openai import (
    OpenAITargetGenerator,
    OpenAITargetGeneratorConfig,
)
from app.infra.llm.target_generator_stub import StubTargetGenerator

# === Meal ===================================================================
# Ports
from app.application.meal.ports.uow_port import MealUnitOfWorkPort

# Use cases
from app.application.meal.use_cases.check_daily_log_completion import (
    CheckDailyLogCompletionUseCase,
)
from app.application.meal.use_cases.create_food_entry import CreateFoodEntryUseCase
from app.application.meal.use_cases.delete_food_entry import DeleteFoodEntryUseCase
from app.application.meal.use_cases.list_food_entries_by_date import (
    ListFoodEntriesByDateUseCase,
)
from app.application.meal.use_cases.update_food_entry import UpdateFoodEntryUseCase

# Infra (repo)
from app.infra.db.uow.meal import SqlAlchemyMealUnitOfWork
from app.infra.meal.meal_entry_query_service import MealEntryQueryService

# === Nutrition ==============================================================
# Ports
from app.application.nutrition.ports.uow_port import NutritionUnitOfWorkPort
from app.application.nutrition.ports.meal_entry_query_port import MealEntryQueryPort
from app.application.nutrition.ports.daily_report_generator_port import (
    DailyNutritionReportGeneratorPort,
)
from app.application.nutrition.ports.nutrition_estimator_port import NutritionEstimatorPort
from app.application.nutrition.ports.recommendation_generator_port import (
    MealRecommendationGeneratorPort,
)

# Use cases
from app.application.nutrition.use_cases.compute_daily_nutrition import (
    ComputeDailyNutritionSummaryUseCase,
)
from app.application.nutrition.use_cases.compute_meal_nutrition import (
    ComputeMealNutritionUseCase,
)
from app.application.nutrition.use_cases.generate_daily_nutrition_report import (
    GenerateDailyNutritionReportUseCase,
)
from app.application.nutrition.use_cases.get_daily_nutrition_report import (
    GetDailyNutritionReportUseCase,
)
from app.application.nutrition.use_cases.get_meal_nutrition import (
    GetMealNutritionUseCase,
)
from app.application.nutrition.use_cases.get_daily_nutrition import (
    GetDailyNutritionUseCase,
)

# infra (estimators / llm)
from app.infra.nutrition.estimator_stub import StubNutritionEstimator
from app.infra.llm.estimator_openai import (
    OpenAINutritionEstimator,
    OpenAINutritionEstimatorConfig,
)

from app.infra.llm.daily_report_generator_openai import (
    OpenAIDailyNutritionReportGenerator,
    OpenAIDailyReportGeneratorConfig,
)
from app.infra.llm.stub_daily_report_generator import (
    StubDailyNutritionReportGenerator,
)

# === Nutrition: MealRecommendation ==========================================
from app.application.nutrition.use_cases.generate_meal_recommendation import (
    GenerateMealRecommendationUseCase,
    GenerateMealRecommendationInput,  # JOB から使うなら import
)
from app.application.nutrition.use_cases.list_meal_recommendations import (
    ListMealRecommendationsUseCase,
)
from app.infra.llm.stub_recommendation_generator import StubMealRecommendationGenerator
from app.infra.llm.meal_recommendation_generator_openai import (
    OpenAIMealRecommendationGenerator,
    OpenAIMealRecommendationGeneratorConfig,
)

# Infra (repos)
from app.infra.db.uow.nutrition import SqlAlchemyNutritionUnitOfWork

# === Calendar ================================================================
# Ports
from app.application.calendar.ports.calendar_unit_of_work_port import CalendarUnitOfWorkPort

# Use cases
from app.application.calendar.use_cases.get_monthly_calendar import GetMonthlyCalendarUseCase

# Infra (uow)
from app.infra.db.uow.calendar import SqlAlchemyCalendarUnitOfWork

# === Billing ================================================================
# Ports
from app.application.billing.ports.uow_port import BillingUnitOfWorkPort
from app.application.billing.ports.stripe_client_port import StripeClientPort

# Use cases
from app.application.billing.use_cases.create_checkout_session import (
    CreateCheckoutSessionUseCase,
)
from app.application.billing.use_cases.get_billing_portal_url import (
    GetBillingPortalUrlUseCase,
)
from app.application.billing.use_cases.handle_stripe_webhook import (
    HandleStripeWebhookUseCase,
)

# Infra (uow / stripe client / repo)
from app.infra.db.uow.billing import SqlAlchemyBillingUnitOfWork
from app.infra.billing.stripe_client import StripeClient

# === Tutorial ===============================================================
# Ports
from app.application.tutorial.ports.tutorial_unit_of_work_port import TutorialUnitOfWorkPort

# Use cases
from app.application.tutorial.use_cases.get_tutorial_status import GetTutorialStatusUseCase
from app.application.tutorial.use_cases.complete_tutorial import CompleteTutorialUseCase

# Infra (repository)
from app.infra.db.uow.tutorial import SqlAlchemyTutorialUnitOfWork


# =============================================================================
# Helpers
# =============================================================================
T = TypeVar("T")


def _resolve_dep(value: object, fallback_factory: Callable[[], T]) -> T:
    """
    FastAPI 経由: value は依存解決済みの実体
    直呼び: value は Depends(...) のマーカー(DependsParam)になっている
    → 直呼び時のみ fallback_factory() で実体化して返す
    """
    if isinstance(value, DependsParam):
        return fallback_factory()
    return cast(T, value)


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in ("1", "true", "yes", "on")


# =============================================================================
# Common / DB / Clock
# =============================================================================
def get_db_session() -> Session:
    # 既存の設計のまま（必要なら他所で利用）
    return create_session()


def get_clock() -> ClockPort:
    return SystemClock()


# =============================================================================
# Auth
# =============================================================================
def get_auth_uow() -> AuthUnitOfWorkPort:
    # UoW は既存のまま（with で session を作って閉じる）
    return SqlAlchemyAuthUnitOfWork()


def get_password_hasher() -> PasswordHasherPort:
    return BcryptPasswordHasher()


def get_token_service() -> TokenServicePort:
    return JwtTokenService()


def get_register_user_use_case(
    uow: AuthUnitOfWorkPort = Depends(get_auth_uow),
    password_hasher: PasswordHasherPort = Depends(get_password_hasher),
    token_service: TokenServicePort = Depends(get_token_service),
    clock: ClockPort = Depends(get_clock),
) -> RegisterUserUseCase:
    uow = _resolve_dep(uow, get_auth_uow)
    password_hasher = _resolve_dep(password_hasher, get_password_hasher)
    token_service = _resolve_dep(token_service, get_token_service)
    clock = _resolve_dep(clock, get_clock)

    return RegisterUserUseCase(
        uow=uow,
        password_hasher=password_hasher,
        token_service=token_service,
        clock=clock,
    )


def get_login_user_use_case(
    uow: AuthUnitOfWorkPort = Depends(get_auth_uow),
    password_hasher: PasswordHasherPort = Depends(get_password_hasher),
    token_service: TokenServicePort = Depends(get_token_service),
) -> LoginUserUseCase:
    uow = _resolve_dep(uow, get_auth_uow)
    password_hasher = _resolve_dep(password_hasher, get_password_hasher)
    token_service = _resolve_dep(token_service, get_token_service)

    return LoginUserUseCase(
        uow=uow,
        password_hasher=password_hasher,
        token_service=token_service,
    )


def get_logout_user_use_case() -> LogoutUserUseCase:
    return LogoutUserUseCase()


def get_delete_account_use_case(
    uow: AuthUnitOfWorkPort = Depends(get_auth_uow),
    clock: ClockPort = Depends(get_clock),
) -> DeleteAccountUseCase:
    uow = _resolve_dep(uow, get_auth_uow)
    clock = _resolve_dep(clock, get_clock)

    return DeleteAccountUseCase(
        uow=uow,
        clock=clock,
    )


def get_refresh_token_use_case(
    uow: AuthUnitOfWorkPort = Depends(get_auth_uow),
    token_service: TokenServicePort = Depends(get_token_service),
) -> RefreshTokenUseCase:
    uow = _resolve_dep(uow, get_auth_uow)
    token_service = _resolve_dep(token_service, get_token_service)

    return RefreshTokenUseCase(
        uow=uow,
        token_service=token_service,
    )


def get_current_user_use_case(
    uow: AuthUnitOfWorkPort = Depends(get_auth_uow),
) -> GetCurrentUserUseCase:
    uow = _resolve_dep(uow, get_auth_uow)
    return GetCurrentUserUseCase(uow=uow)


# ✅ UoW を抱える singleton は廃止（毎回生成）
def get_plan_checker(
    auth_uow: AuthUnitOfWorkPort = Depends(get_auth_uow),
    clock: ClockPort = Depends(get_clock),
) -> PlanCheckerPort:
    auth_uow = _resolve_dep(auth_uow, get_auth_uow)
    clock = _resolve_dep(clock, get_clock)

    return PlanCheckerService(
        auth_uow=auth_uow,
        clock=clock,
    )


# =============================================================================
# Profile
# =============================================================================
_profile_image_storage_singleton: ProfileImageStoragePort | None = None


def get_profile_image_storage() -> ProfileImageStoragePort:
    global _profile_image_storage_singleton

    if _profile_image_storage_singleton is None:
        if settings.USE_FAKE_INFRA:
            _profile_image_storage_singleton = InMemoryProfileImageStorage()
        else:
            _profile_image_storage_singleton = MinioProfileImageStorage()
    return _profile_image_storage_singleton


def get_profile_uow() -> ProfileUnitOfWorkPort:
    return SqlAlchemyProfileUnitOfWork()


def get_upsert_profile_use_case(
    uow: ProfileUnitOfWorkPort = Depends(get_profile_uow),
    image_storage: ProfileImageStoragePort = Depends(
        get_profile_image_storage),
) -> UpsertProfileUseCase:
    uow = _resolve_dep(uow, get_profile_uow)
    image_storage = _resolve_dep(image_storage, get_profile_image_storage)

    return UpsertProfileUseCase(
        uow=uow,
        image_storage=image_storage,
    )


def get_my_profile_use_case(
    uow: ProfileUnitOfWorkPort = Depends(get_profile_uow),
) -> GetMyProfileUseCase:
    uow = _resolve_dep(uow, get_profile_uow)
    return GetMyProfileUseCase(uow=uow)


def get_profile_query_service(
    get_my_profile_uc: GetMyProfileUseCase = Depends(get_my_profile_use_case),
) -> ProfileQueryPort:
    get_my_profile_uc = _resolve_dep(
        get_my_profile_uc, get_my_profile_use_case)
    return ProfileQueryService(get_my_profile_uc=get_my_profile_uc)


# =============================================================================
# Target
# =============================================================================
def get_target_uow() -> TargetUnitOfWorkPort:
    return SqlAlchemyTargetUnitOfWork()


_target_generator_singleton: TargetGeneratorPort | None = None


def get_target_generator() -> TargetGeneratorPort:
    """
    ✅ env フラグは「初回呼び出し時」に読む（import時確定をやめる）
    """
    global _target_generator_singleton
    if _target_generator_singleton is None:
        use_openai = _env_bool("USE_OPENAI_TARGET_GENERATOR", default=False)
        if use_openai:
            _target_generator_singleton = OpenAITargetGenerator(
                config=OpenAITargetGeneratorConfig(
                    model=os.getenv("OPENAI_TARGET_MODEL", "gpt-4o-mini"),
                    temperature=float(
                        os.getenv("OPENAI_TARGET_TEMPERATURE", "0.2")),
                )
            )
        else:
            _target_generator_singleton = StubTargetGenerator()
    return _target_generator_singleton


def get_create_target_use_case(
    uow: TargetUnitOfWorkPort = Depends(get_target_uow),
    generator: TargetGeneratorPort = Depends(get_target_generator),
    profile_query: ProfileQueryPort = Depends(get_profile_query_service),
    clock: ClockPort = Depends(get_clock),
) -> CreateTargetUseCase:
    uow = _resolve_dep(uow, get_target_uow)
    generator = _resolve_dep(generator, get_target_generator)
    profile_query = _resolve_dep(profile_query, get_profile_query_service)
    clock = _resolve_dep(clock, get_clock)

    return CreateTargetUseCase(
        uow=uow,
        generator=generator,
        profile_query=profile_query,
        clock=clock,
    )


def get_get_active_target_use_case(
    uow: TargetUnitOfWorkPort = Depends(get_target_uow),
) -> GetActiveTargetUseCase:
    uow = _resolve_dep(uow, get_target_uow)
    return GetActiveTargetUseCase(uow=uow)


def get_list_targets_use_case(
    uow: TargetUnitOfWorkPort = Depends(get_target_uow),
) -> ListTargetsUseCase:
    uow = _resolve_dep(uow, get_target_uow)
    return ListTargetsUseCase(uow=uow)


def get_activate_target_use_case(
    uow: TargetUnitOfWorkPort = Depends(get_target_uow),
) -> ActivateTargetUseCase:
    uow = _resolve_dep(uow, get_target_uow)
    return ActivateTargetUseCase(uow=uow)


def get_update_target_use_case(
    uow: TargetUnitOfWorkPort = Depends(get_target_uow),
) -> UpdateTargetUseCase:
    uow = _resolve_dep(uow, get_target_uow)
    return UpdateTargetUseCase(uow=uow)


def get_get_target_use_case(
    uow: TargetUnitOfWorkPort = Depends(get_target_uow),
) -> GetTargetUseCase:
    uow = _resolve_dep(uow, get_target_uow)
    return GetTargetUseCase(uow=uow)


def get_delete_target_use_case(
    uow: TargetUnitOfWorkPort = Depends(get_target_uow),
) -> DeleteTargetUseCase:
    uow = _resolve_dep(uow, get_target_uow)
    return DeleteTargetUseCase(uow=uow)


# =============================================================================
# Meal
# =============================================================================
def get_meal_uow() -> MealUnitOfWorkPort:
    return SqlAlchemyMealUnitOfWork()


def get_create_food_entry_use_case(
    meal_uow: MealUnitOfWorkPort = Depends(get_meal_uow),
) -> CreateFoodEntryUseCase:
    meal_uow = _resolve_dep(meal_uow, get_meal_uow)
    return CreateFoodEntryUseCase(meal_uow=meal_uow)


def get_update_food_entry_use_case(
    meal_uow: MealUnitOfWorkPort = Depends(get_meal_uow),
) -> UpdateFoodEntryUseCase:
    meal_uow = _resolve_dep(meal_uow, get_meal_uow)
    return UpdateFoodEntryUseCase(meal_uow=meal_uow)


def get_delete_food_entry_use_case(
    meal_uow: MealUnitOfWorkPort = Depends(get_meal_uow),
) -> DeleteFoodEntryUseCase:
    meal_uow = _resolve_dep(meal_uow, get_meal_uow)
    return DeleteFoodEntryUseCase(meal_uow=meal_uow)


def get_list_food_entries_by_date_use_case(
    meal_uow: MealUnitOfWorkPort = Depends(get_meal_uow),
) -> ListFoodEntriesByDateUseCase:
    meal_uow = _resolve_dep(meal_uow, get_meal_uow)
    return ListFoodEntriesByDateUseCase(meal_uow=meal_uow)


def get_meal_entry_query_service(
    meal_uow: MealUnitOfWorkPort = Depends(get_meal_uow),
) -> MealEntryQueryPort:
    meal_uow = _resolve_dep(meal_uow, get_meal_uow)
    return MealEntryQueryService(meal_uow=meal_uow)


# =============================================================================
# Nutrition
# =============================================================================
def get_nutrition_uow() -> NutritionUnitOfWorkPort:
    return SqlAlchemyNutritionUnitOfWork()


_nutrition_estimator_singleton: NutritionEstimatorPort | None = None


def get_nutrition_estimator() -> NutritionEstimatorPort:
    """
    ✅ env フラグは「初回呼び出し時」に読む
    """
    global _nutrition_estimator_singleton
    if _nutrition_estimator_singleton is None:
        use_openai = _env_bool("USE_OPENAI_NUTRITION_ESTIMATOR", default=False)
        if use_openai:
            _nutrition_estimator_singleton = OpenAINutritionEstimator(
                config=OpenAINutritionEstimatorConfig(
                    model=os.getenv("OPENAI_NUTRITION_MODEL", "gpt-4o-mini"),
                    temperature=float(
                        os.getenv("OPENAI_NUTRITION_TEMPERATURE", "0.1")),
                )
            )
        else:
            _nutrition_estimator_singleton = StubNutritionEstimator()
    return _nutrition_estimator_singleton


def get_compute_meal_nutrition_use_case(
    meal_entry_query_service: MealEntryQueryPort = Depends(
        get_meal_entry_query_service),
    nutrition_uow: NutritionUnitOfWorkPort = Depends(get_nutrition_uow),
    estimator: NutritionEstimatorPort = Depends(get_nutrition_estimator),
    plan_checker: PlanCheckerPort = Depends(get_plan_checker),
) -> ComputeMealNutritionUseCase:
    meal_entry_query_service = _resolve_dep(
        meal_entry_query_service, get_meal_entry_query_service)
    nutrition_uow = _resolve_dep(nutrition_uow, get_nutrition_uow)
    estimator = _resolve_dep(estimator, get_nutrition_estimator)
    plan_checker = _resolve_dep(plan_checker, get_plan_checker)

    return ComputeMealNutritionUseCase(
        meal_entry_query_service=meal_entry_query_service,
        nutrition_uow=nutrition_uow,
        estimator=estimator,
        plan_checker=plan_checker,
    )


def get_compute_daily_nutrition_summary_use_case(
    uow: NutritionUnitOfWorkPort = Depends(get_nutrition_uow),
    plan_checker: PlanCheckerPort = Depends(get_plan_checker),
) -> ComputeDailyNutritionSummaryUseCase:
    uow = _resolve_dep(uow, get_nutrition_uow)
    plan_checker = _resolve_dep(plan_checker, get_plan_checker)

    return ComputeDailyNutritionSummaryUseCase(
        uow=uow,
        plan_checker=plan_checker,
    )


def get_get_meal_nutrition_use_case(
    nutrition_uow: NutritionUnitOfWorkPort = Depends(get_nutrition_uow),
    plan_checker: PlanCheckerPort = Depends(get_plan_checker),
) -> GetMealNutritionUseCase:
    nutrition_uow = _resolve_dep(nutrition_uow, get_nutrition_uow)
    plan_checker = _resolve_dep(plan_checker, get_plan_checker)

    return GetMealNutritionUseCase(
        nutrition_uow=nutrition_uow,
        plan_checker=plan_checker,
    )


def get_get_daily_nutrition_use_case(
    nutrition_uow: NutritionUnitOfWorkPort = Depends(get_nutrition_uow),
    plan_checker: PlanCheckerPort = Depends(get_plan_checker),
) -> GetDailyNutritionUseCase:
    nutrition_uow = _resolve_dep(nutrition_uow, get_nutrition_uow)
    plan_checker = _resolve_dep(plan_checker, get_plan_checker)

    return GetDailyNutritionUseCase(
        nutrition_uow=nutrition_uow,
        plan_checker=plan_checker,
    )


_daily_report_generator_singleton: DailyNutritionReportGeneratorPort | None = None


def get_daily_nutrition_report_generator() -> DailyNutritionReportGeneratorPort:
    """
    ✅ env フラグは「初回呼び出し時」に読む
    """
    global _daily_report_generator_singleton
    if _daily_report_generator_singleton is None:
        use_openai = _env_bool(
            "USE_OPENAI_DAILY_REPORT_GENERATOR", default=False)
        if use_openai:
            model = os.getenv("OPENAI_DAILY_REPORT_MODEL", "gpt-4o-mini")
            temperature = float(
                os.getenv("OPENAI_DAILY_REPORT_TEMPERATURE", "0.4"))
            _daily_report_generator_singleton = OpenAIDailyNutritionReportGenerator(
                config=OpenAIDailyReportGeneratorConfig(
                    model=model,
                    temperature=temperature,
                )
            )
        else:
            _daily_report_generator_singleton = StubDailyNutritionReportGenerator()
    return _daily_report_generator_singleton


def get_check_daily_log_completion_use_case(
    profile_query: ProfileQueryPort = Depends(get_profile_query_service),
    meal_uow: MealUnitOfWorkPort = Depends(get_meal_uow),
) -> CheckDailyLogCompletionUseCase:
    profile_query = _resolve_dep(profile_query, get_profile_query_service)
    meal_uow = _resolve_dep(meal_uow, get_meal_uow)

    return CheckDailyLogCompletionUseCase(
        profile_query=profile_query,
        meal_uow=meal_uow,
    )


def get_ensure_daily_target_snapshot_use_case(
    uow: TargetUnitOfWorkPort = Depends(get_target_uow),
) -> EnsureDailyTargetSnapshotUseCase:
    uow = _resolve_dep(uow, get_target_uow)
    return EnsureDailyTargetSnapshotUseCase(uow=uow)


def get_generate_daily_nutrition_report_use_case(
    daily_log_uc: CheckDailyLogCompletionUseCase = Depends(
        get_check_daily_log_completion_use_case),
    profile_query: ProfileQueryPort = Depends(get_profile_query_service),
    ensure_target_snapshot_uc: EnsureDailyTargetSnapshotUseCase = Depends(
        get_ensure_daily_target_snapshot_use_case),
    daily_nutrition_uc: ComputeDailyNutritionSummaryUseCase = Depends(
        get_compute_daily_nutrition_summary_use_case),
    nutrition_uow: NutritionUnitOfWorkPort = Depends(get_nutrition_uow),
    report_generator: DailyNutritionReportGeneratorPort = Depends(
        get_daily_nutrition_report_generator),
    clock: ClockPort = Depends(get_clock),
) -> GenerateDailyNutritionReportUseCase:
    daily_log_uc = _resolve_dep(
        daily_log_uc, get_check_daily_log_completion_use_case)
    profile_query = _resolve_dep(profile_query, get_profile_query_service)
    ensure_target_snapshot_uc = _resolve_dep(
        ensure_target_snapshot_uc, get_ensure_daily_target_snapshot_use_case)
    daily_nutrition_uc = _resolve_dep(
        daily_nutrition_uc, get_compute_daily_nutrition_summary_use_case)
    nutrition_uow = _resolve_dep(nutrition_uow, get_nutrition_uow)
    report_generator = _resolve_dep(
        report_generator, get_daily_nutrition_report_generator)
    clock = _resolve_dep(clock, get_clock)

    return GenerateDailyNutritionReportUseCase(
        daily_log_uc=daily_log_uc,
        profile_query=profile_query,
        ensure_target_snapshot_uc=ensure_target_snapshot_uc,
        daily_nutrition_uc=daily_nutrition_uc,
        nutrition_uow=nutrition_uow,
        report_generator=report_generator,
        clock=clock,
    )


def get_get_daily_nutrition_report_use_case(
    uow: NutritionUnitOfWorkPort = Depends(get_nutrition_uow),
) -> GetDailyNutritionReportUseCase:
    uow = _resolve_dep(uow, get_nutrition_uow)
    return GetDailyNutritionReportUseCase(uow=uow)


# =============================================================================
# MealRecommendation
# =============================================================================
_recommendation_generator_singleton: MealRecommendationGeneratorPort | None = None


def get_meal_recommendation_generator() -> MealRecommendationGeneratorPort:
    """
    ✅ env フラグは「初回呼び出し時」に読む
    """
    global _recommendation_generator_singleton
    if _recommendation_generator_singleton is None:
        use_openai = _env_bool(
            "USE_OPENAI_MEAL_RECOMMENDATION_GENERATOR", default=False)
        if use_openai:
            model = os.getenv(
                "OPENAI_MEAL_RECOMMENDATION_MODEL", "gpt-4o-mini")
            temperature = float(
                os.getenv("OPENAI_MEAL_RECOMMENDATION_TEMPERATURE", "0.4"))
            _recommendation_generator_singleton = OpenAIMealRecommendationGenerator(
                config=OpenAIMealRecommendationGeneratorConfig(
                    model=model,
                    temperature=temperature,
                )
            )
        else:
            _recommendation_generator_singleton = StubMealRecommendationGenerator()
    return _recommendation_generator_singleton


def get_generate_meal_recommendation_use_case(
    profile_query: ProfileQueryPort = Depends(get_profile_query_service),
    nutrition_uow: NutritionUnitOfWorkPort = Depends(get_nutrition_uow),
    generator: MealRecommendationGeneratorPort = Depends(
        get_meal_recommendation_generator),
    clock: ClockPort = Depends(get_clock),
    plan_checker: PlanCheckerPort = Depends(get_plan_checker),
) -> GenerateMealRecommendationUseCase:
    profile_query = _resolve_dep(profile_query, get_profile_query_service)
    nutrition_uow = _resolve_dep(nutrition_uow, get_nutrition_uow)
    generator = _resolve_dep(generator, get_meal_recommendation_generator)
    clock = _resolve_dep(clock, get_clock)
    plan_checker = _resolve_dep(plan_checker, get_plan_checker)

    cooldown_minutes = int(os.getenv("MEAL_RECOMMENDATION_COOLDOWN_MINUTES", "30"))
    daily_limit = int(os.getenv("MEAL_RECOMMENDATION_DAILY_LIMIT", "5"))

    # デバッグログ: 実際に読み込まれた制限値を出力
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"MealRecommendation settings: cooldown_minutes={cooldown_minutes}, daily_limit={daily_limit}")

    return GenerateMealRecommendationUseCase(
        profile_query=profile_query,
        nutrition_uow=nutrition_uow,
        generator=generator,
        clock=clock,
        min_required_days=1,
        max_lookup_days=5,
        plan_checker=plan_checker,
        cooldown_minutes=cooldown_minutes,
        daily_limit=daily_limit,
    )


def get_list_meal_recommendations_use_case(
    nutrition_uow: NutritionUnitOfWorkPort = Depends(get_nutrition_uow),
    plan_checker: PlanCheckerPort = Depends(get_plan_checker),
) -> ListMealRecommendationsUseCase:
    nutrition_uow = _resolve_dep(nutrition_uow, get_nutrition_uow)
    plan_checker = _resolve_dep(plan_checker, get_plan_checker)
    return ListMealRecommendationsUseCase(
        nutrition_uow=nutrition_uow,
        plan_checker=plan_checker,
    )


# =============================================================================
# Billing
# =============================================================================
_stripe_client_singleton: StripeClientPort | None = None


def get_stripe_client() -> StripeClientPort:
    # StripeClient は DB/UoW を抱えないので singleton 維持でOK
    global _stripe_client_singleton
    if _stripe_client_singleton is None:
        _stripe_client_singleton = StripeClient()
    return _stripe_client_singleton


def get_billing_uow() -> BillingUnitOfWorkPort:
    return SqlAlchemyBillingUnitOfWork()


def get_create_checkout_session_use_case(
    billing_uow: BillingUnitOfWorkPort = Depends(get_billing_uow),
    auth_uow: AuthUnitOfWorkPort = Depends(get_auth_uow),
    stripe_client: StripeClientPort = Depends(get_stripe_client),
    clock: ClockPort = Depends(get_clock),
) -> CreateCheckoutSessionUseCase:
    billing_uow = _resolve_dep(billing_uow, get_billing_uow)
    auth_uow = _resolve_dep(auth_uow, get_auth_uow)
    stripe_client = _resolve_dep(stripe_client, get_stripe_client)
    clock = _resolve_dep(clock, get_clock)

    return CreateCheckoutSessionUseCase(
        billing_uow=billing_uow,
        auth_uow=auth_uow,
        stripe_client=stripe_client,
        clock=clock,
        price_id=settings.STRIPE_PRICE_ID,
    )


def get_billing_portal_url_use_case(
    billing_uow: BillingUnitOfWorkPort = Depends(get_billing_uow),
    stripe_client: StripeClientPort = Depends(get_stripe_client),
) -> GetBillingPortalUrlUseCase:
    billing_uow = _resolve_dep(billing_uow, get_billing_uow)
    stripe_client = _resolve_dep(stripe_client, get_stripe_client)

    return GetBillingPortalUrlUseCase(
        billing_uow=billing_uow,
        stripe_client=stripe_client,
    )


def get_handle_stripe_webhook_use_case(
    billing_uow: BillingUnitOfWorkPort = Depends(get_billing_uow),
    auth_uow: AuthUnitOfWorkPort = Depends(get_auth_uow),
    stripe_client: StripeClientPort = Depends(get_stripe_client),
    clock: ClockPort = Depends(get_clock),
) -> HandleStripeWebhookUseCase:
    billing_uow = _resolve_dep(billing_uow, get_billing_uow)
    auth_uow = _resolve_dep(auth_uow, get_auth_uow)
    stripe_client = _resolve_dep(stripe_client, get_stripe_client)
    clock = _resolve_dep(clock, get_clock)

    return HandleStripeWebhookUseCase(
        billing_uow=billing_uow,
        auth_uow=auth_uow,
        stripe_client=stripe_client,
        clock=clock,
    )


# =============================================================================
# Calendar
# =============================================================================
def get_calendar_uow() -> CalendarUnitOfWorkPort:
    return SqlAlchemyCalendarUnitOfWork()


def get_get_monthly_calendar_use_case(
    uow: CalendarUnitOfWorkPort = Depends(get_calendar_uow),
) -> GetMonthlyCalendarUseCase:
    uow = _resolve_dep(uow, get_calendar_uow)
    return GetMonthlyCalendarUseCase(uow=uow)


# =============================================================================
# Tutorial
# =============================================================================
def get_tutorial_uow() -> TutorialUnitOfWorkPort:
    """チュートリアルUnit of Workを取得"""
    return SqlAlchemyTutorialUnitOfWork(create_session)


def get_get_tutorial_status_use_case(
    tutorial_uow: TutorialUnitOfWorkPort = Depends(get_tutorial_uow),
) -> GetTutorialStatusUseCase:
    """チュートリアル状況取得ユースケースを取得"""
    tutorial_uow = _resolve_dep(tutorial_uow, get_tutorial_uow)
    return GetTutorialStatusUseCase(tutorial_uow)


def get_complete_tutorial_use_case(
    tutorial_uow: TutorialUnitOfWorkPort = Depends(get_tutorial_uow),
) -> CompleteTutorialUseCase:
    """チュートリアル完了ユースケースを取得"""
    tutorial_uow = _resolve_dep(tutorial_uow, get_tutorial_uow)
    return CompleteTutorialUseCase(tutorial_uow)
