from __future__ import annotations

# === Standard library =======================================================
import os

# === Third-party ============================================================
from fastapi import Depends
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
from app.application.auth.ports.user_repository_port import UserRepositoryPort

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
from app.infra.db.repositories.user_repository import SqlAlchemyUserRepository
from app.infra.db.uow.auth import SqlAlchemyAuthUnitOfWork
from app.infra.security.jwt_token_service import JwtTokenService
from app.infra.security.password_hasher import BcryptPasswordHasher

# === Profile ================================================================
# Ports
from app.application.profile.ports.profile_image_storage_port import (
    ProfileImageStoragePort,
)
from app.application.profile.ports.profile_repository_port import ProfileRepositoryPort
from app.application.profile.ports.uow_port import ProfileUnitOfWorkPort

# Use cases
from app.application.profile.use_cases.get_my_profile import GetMyProfileUseCase
from app.application.profile.use_cases.upsert_profile import UpsertProfileUseCase

# Infra (repo / uow / storage / query service)
from app.infra.db.repositories.profile_repository import SqlAlchemyProfileRepository
from app.infra.db.uow.profile import SqlAlchemyProfileUnitOfWork
from app.infra.profile.profile_query_service import ProfileQueryService
from app.infra.storage.minio_profile_image_storage import MinioProfileImageStorage
from app.infra.storage.profile_image_storage import InMemoryProfileImageStorage

# === Target ================================================================
# Ports
from app.application.target.ports.target_generator_port import TargetGeneratorPort
from app.application.target.ports.target_repository_port import TargetRepositoryPort
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

# Infra (repo / uow / llm)
from app.infra.db.repositories.target_repository import SqlAlchemyTargetRepository
from app.infra.db.uow.target import SqlAlchemyTargetUnitOfWork
from app.infra.llm.target_generator_openai import (
    OpenAITargetGenerator,
    OpenAITargetGeneratorConfig,
)
from app.infra.llm.target_generator_stub import StubTargetGenerator

# === Meal ===================================================================
# Ports
from app.application.meal.ports.food_entry_repository_port import FoodEntryRepositoryPort
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
from app.infra.db.repositories.food_entry_repository import SqlAlchemyFoodEntryRepository
from app.infra.db.uow.meal import SqlAlchemyMealUnitOfWork
from app.infra.meal.meal_entry_query_service import MealEntryQueryService

# === Nutrition ==============================================================
# Ports
from app.application.nutrition.ports.uow_port import NutritionUnitOfWorkPort
from app.application.nutrition.ports.meal_entry_query_port import MealEntryQueryPort

from app.application.nutrition.ports.daily_nutrition_repository_port import (
    DailyNutritionSummaryRepositoryPort,
)
from app.application.nutrition.ports.daily_report_generator_port import (
    DailyNutritionReportGeneratorPort,
)
from app.application.nutrition.ports.daily_report_repository_port import (
    DailyNutritionReportRepositoryPort,
)
from app.application.nutrition.ports.meal_nutrition_repository_port import (
    MealNutritionSummaryRepositoryPort,
)
from app.application.nutrition.ports.nutrition_estimator_port import NutritionEstimatorPort
from app.application.nutrition.ports.recommendation_generator_port import (
    MealRecommendationGeneratorPort,
)
from app.application.nutrition.ports.recommendation_repository_port import (
    MealRecommendationRepositoryPort,
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
from app.application.nutrition.use_cases.generate_meal_recommendation import (
    GenerateMealRecommendationUseCase,
)


# Infra (repos)
from app.infra.db.uow.nutrition import SqlAlchemyNutritionUnitOfWork

from app.infra.db.repositories.daily_nutrition_report_repository import (
    SqlAlchemyDailyNutritionReportRepository,
)
from app.infra.db.repositories.daily_nutrition_repository import (
    SqlAlchemyDailyNutritionSummaryRepository,
)
from app.infra.db.repositories.meal_nutrition_repository import (
    SqlAlchemyMealNutritionSummaryRepository,
)
# from app.infra.db.repositories.recommendation_repository import (
#     SqlAlchemyMealRecommendationRepository,
# )

# LLM / estimators
from app.infra.llm.stub_daily_report_generator import (
    StubDailyNutritionReportGenerator,
)
from app.infra.llm.stub_recommendation_generator import StubMealRecommendationGenerator
from app.infra.nutrition.estimator_stub import StubNutritionEstimator


# === Common / DB / UoW =====================================================
# アプリ全体で共通して使うインフラ（DBセッション / Clock など）の提供

# DBセッションを1つ生成して返す（各 Repository で利用する）
def get_db_session() -> Session:
    return create_session()


# 現在時刻を提供する ClockPort の実装を返す
def get_clock() -> ClockPort:
    return SystemClock()


# === Auth ===================================================================
# 認証・認可（ユーザー登録 / ログイン / トークン）関連の DI 定義

# 認証コンテキスト用の UnitOfWork 実装を返す
def get_auth_uow() -> AuthUnitOfWorkPort:
    return SqlAlchemyAuthUnitOfWork()


# パスワードのハッシュ化ロジック（Bcrypt）の実装を返す
def get_password_hasher() -> PasswordHasherPort:
    return BcryptPasswordHasher()


# アクセストークン / リフレッシュトークンを扱うサービスの実装を返す
def get_token_service() -> TokenServicePort:
    return JwtTokenService()


# ユーザー登録 UseCase 用の依存を組み立てて返す
def get_register_user_use_case() -> RegisterUserUseCase:
    return RegisterUserUseCase(
        uow=get_auth_uow(),
        password_hasher=get_password_hasher(),
        token_service=get_token_service(),
        clock=get_clock(),
    )


# ログイン UseCase 用の依存を組み立てて返す
def get_login_user_use_case() -> LoginUserUseCase:
    return LoginUserUseCase(
        uow=get_auth_uow(),
        password_hasher=get_password_hasher(),
        token_service=get_token_service(),
    )


# ログアウト UseCase（今は stateless）を返す
def get_logout_user_use_case() -> LogoutUserUseCase:
    return LogoutUserUseCase()


# アカウント削除 UseCase 用の依存を組み立てて返す
def get_delete_account_use_case() -> DeleteAccountUseCase:
    return DeleteAccountUseCase(
        uow=get_auth_uow(),
        clock=get_clock(),
    )


# リフレッシュトークン発行 UseCase 用の依存を組み立てて返す
def get_refresh_token_use_case() -> RefreshTokenUseCase:
    return RefreshTokenUseCase(
        uow=get_auth_uow(),
        token_service=get_token_service(),
    )


# 現在ログイン中のユーザーを取得する UseCase の DI
def get_current_user_use_case() -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(
        uow=get_auth_uow(),
    )


# === Profile ================================================================
# プロフィール情報とプロフィール画像ストレージまわりの DI 定義

# プロフィール画像ストレージ（MinIO / InMemory）のシングルトンインスタンス
_profile_image_storage_singleton: ProfileImageStoragePort | None = None


# プロフィール画像の保存先（MinIO or InMemory）の実装を返す
def get_profile_image_storage() -> ProfileImageStoragePort:
    global _profile_image_storage_singleton

    if _profile_image_storage_singleton is None:
        if settings.USE_FAKE_INFRA:
            _profile_image_storage_singleton = InMemoryProfileImageStorage()
        else:
            _profile_image_storage_singleton = MinioProfileImageStorage()
    return _profile_image_storage_singleton


# プロフィール更新用の UnitOfWork 実装を返す
def get_profile_uow() -> ProfileUnitOfWorkPort:
    return SqlAlchemyProfileUnitOfWork()


# プロフィールを新規作成・更新する UseCase の DI
def get_upsert_profile_use_case() -> UpsertProfileUseCase:
    return UpsertProfileUseCase(
        uow=get_profile_uow(),
        image_storage=get_profile_image_storage(),
    )


# 自分自身のプロフィールを取得する UseCase の DI
def get_my_profile_use_case() -> GetMyProfileUseCase:
    return GetMyProfileUseCase(
        uow=get_profile_uow(),
    )


# === Target ================================================================
# 目標（Target）と DailyTargetSnapshot まわりの DI 定義

# 目標情報を扱う UnitOfWork 実装を返す
def get_target_uow() -> TargetUnitOfWorkPort:
    return SqlAlchemyTargetUnitOfWork()


# 目標自動生成ロジック（Stub / OpenAI）のシングルトンインスタンス
_target_generator_singleton: TargetGeneratorPort | None = None

# OpenAI の TargetGenerator を使うかどうかのフラグ
_USE_OPENAI_TARGET_GENERATOR = os.getenv(
    "USE_OPENAI_TARGET_GENERATOR", "false"
).lower() in ("1", "true", "yes", "on")


# 目標を自動生成する TargetGeneratorPort の実装を返す
def get_target_generator() -> TargetGeneratorPort:
    global _target_generator_singleton

    if _target_generator_singleton is None:
        if _USE_OPENAI_TARGET_GENERATOR:
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


# プロフィール情報取得用の QueryService を返す
def get_profile_query_service() -> ProfileQueryService:
    return ProfileQueryService(
        get_my_profile_uc=get_my_profile_use_case(),
    )


# 新しい Target を作成する UseCase の DI
def get_create_target_use_case() -> CreateTargetUseCase:
    """
    /target/create のための UseCase を DI する。
    """
    return CreateTargetUseCase(
        uow=get_target_uow(),
        generator=get_target_generator(),
        profile_query=get_profile_query_service(),
    )


# アクティブな Target を取得する UseCase の DI
def get_get_active_target_use_case() -> GetActiveTargetUseCase:
    """
    /target/active（現在のターゲット取得）のための UseCase。
    """
    return GetActiveTargetUseCase(
        uow=get_target_uow(),
    )


# Target 一覧を取得する UseCase の DI
def get_list_targets_use_case() -> ListTargetsUseCase:
    """
    /target/list のための UseCase。
    """
    return ListTargetsUseCase(
        uow=get_target_uow(),
    )


# Target を有効化（activate）する UseCase の DI
def get_activate_target_use_case() -> ActivateTargetUseCase:
    """
    /target/activate のための UseCase。
    """
    return ActivateTargetUseCase(
        uow=get_target_uow(),
        clock=get_clock(),
    )


# 既存の Target を更新する UseCase の DI
def get_update_target_use_case() -> UpdateTargetUseCase:
    """
    /target/update のための UseCase。
    """
    return UpdateTargetUseCase(
        uow=get_target_uow(),
        clock=get_clock(),
    )


# 特定の Target を取得する UseCase の DI
def get_get_target_use_case() -> GetTargetUseCase:
    """
    /target/get のための UseCase。
    """
    return GetTargetUseCase(
        uow=get_target_uow(),
    )


# === Meal ===================================================================
# 食事記録（FoodEntry）まわりの DI 定義

# 食事エントリを扱う Repository を返す
def get_meal_uow() -> MealUnitOfWorkPort:
    return SqlAlchemyMealUnitOfWork()


# 食事エントリの作成 UseCase の DI
def get_create_food_entry_use_case() -> CreateFoodEntryUseCase:
    return CreateFoodEntryUseCase(
        meal_uow=get_meal_uow(),
    )


# 食事エントリの更新 UseCase の DI
def get_update_food_entry_use_case() -> UpdateFoodEntryUseCase:
    return UpdateFoodEntryUseCase(
        meal_uow=get_meal_uow(),
    )


# 食事エントリの削除 UseCase の DI
def get_delete_food_entry_use_case() -> DeleteFoodEntryUseCase:
    return DeleteFoodEntryUseCase(
        meal_uow=get_meal_uow(),
    )


# 指定日の食事エントリ一覧を取得する UseCase の DI
def get_list_food_entries_by_date_use_case() -> ListFoodEntriesByDateUseCase:
    return ListFoodEntriesByDateUseCase(
        meal_uow=get_meal_uow(),
    )


# === Nutrition: estimator & repositories ====================================
# 栄養推定ロジックと栄養サマリ系 Repository の DI 定義

# NutritionUnitOfWork を返す
def get_nutrition_uow() -> NutritionUnitOfWorkPort:
    """
    栄養ドメイン用 UnitOfWork 実装を返す。
    """
    return SqlAlchemyNutritionUnitOfWork()


# 栄養推定ロジック（Stub）の実装を返す
def get_nutrition_estimator() -> NutritionEstimatorPort:
    """
    栄養推定ロジック。

    - MVP では StubNutritionEstimator を利用
    - 後で LLM / 外部DB 実装に差し替え可能
    """
    return StubNutritionEstimator()


def get_meal_entry_query_service() -> MealEntryQueryPort:
    return MealEntryQueryService(
        meal_uow=get_meal_uow(),
    )


# === Nutrition: core use cases ==============================================
# Meal単位 / 日単位の栄養計算 UseCase の DI 定義

# 1 Meal 分の栄養を推定し、MealNutritionSummary を更新する UseCase の DI
def get_compute_meal_nutrition_use_case() -> ComputeMealNutritionUseCase:
    """
    1 Meal 分の栄養を推定して MealNutritionSummary を更新する UseCase。
    """
    meal_entry_query_service = get_meal_entry_query_service()
    nutrition_uow = get_nutrition_uow()
    estimator = get_nutrition_estimator()

    return ComputeMealNutritionUseCase(
        meal_entry_query_service=meal_entry_query_service,
        nutrition_uow=nutrition_uow,
        estimator=estimator,
    )


# 1 日分の栄養サマリ（DailyNutritionSummary）を計算・保存する UseCase の DI
def get_compute_daily_nutrition_summary_use_case(
) -> ComputeDailyNutritionSummaryUseCase:
    """
    1日分の栄養サマリ (DailyNutritionSummary) を計算・保存する UC。

    - MealNutritionSummary を集約して計算する。
    """
    return ComputeDailyNutritionSummaryUseCase(
        uow=get_nutrition_uow(),
    )


# === DailyNutritionReport ====================================================
# 日次栄養レポート生成まわりの DI 定義

# 日次レポート生成用 LLM ポートのシングルトンインスタンス
_daily_report_generator_singleton: DailyNutritionReportGeneratorPort | None = None


# 日次栄養レポートを文章として生成する Generator の実装を返す
def get_daily_nutrition_report_generator() -> DailyNutritionReportGeneratorPort:
    """
    日次レポート生成用 LLM ポートの DI。

    - 現時点では StubDailyNutritionReportGenerator をシングルトンで返す。
    - 後で OpenAI 実装に差し替えるときはここを書き換える。
    """
    global _daily_report_generator_singleton
    if _daily_report_generator_singleton is None:
        _daily_report_generator_singleton = StubDailyNutritionReportGenerator()
    return _daily_report_generator_singleton


# DailyNutritionReport を扱う Repository を返す
def get_daily_nutrition_report_repository(
    session: Session | None = None,
) -> DailyNutritionReportRepositoryPort:
    if session is None:
        session = get_db_session()
    return SqlAlchemyDailyNutritionReportRepository(session)


# 1 日分の食事ログが「記録完了」かどうか判定する UseCase の DI
def get_check_daily_log_completion_use_case() -> CheckDailyLogCompletionUseCase:
    """
    1 日分の食事ログが「記録完了」しているかを判定する UseCase の DI。
    """
    return CheckDailyLogCompletionUseCase(
        profile_query=get_profile_query_service(),
        meal_uow=get_meal_uow(),
    )


# DailyTargetSnapshot を確保する UseCase の DI
def get_ensure_daily_target_snapshot_use_case() -> EnsureDailyTargetSnapshotUseCase:
    """
    DailyTargetSnapshot 用 UseCase の DI。
    """
    return EnsureDailyTargetSnapshotUseCase(
        uow=get_target_uow(),
    )


# 日次栄養レポート（DailyNutritionReport）を生成する UseCase の DI
def get_generate_daily_nutrition_report_use_case(
) -> GenerateDailyNutritionReportUseCase:
    daily_log_uc = get_check_daily_log_completion_use_case()
    ensure_target_snapshot_uc = get_ensure_daily_target_snapshot_use_case()
    daily_nutrition_uc = get_compute_daily_nutrition_summary_use_case()
    report_generator = get_daily_nutrition_report_generator()
    clock = get_clock()

    return GenerateDailyNutritionReportUseCase(
        daily_log_uc=daily_log_uc,
        profile_query=get_profile_query_service(),
        ensure_target_snapshot_uc=ensure_target_snapshot_uc,
        daily_nutrition_uc=daily_nutrition_uc,
        nutrition_uow=get_nutrition_uow(),
        report_generator=report_generator,
        clock=clock,
    )


# 指定した (user_id, date) の DailyNutritionReport を取得する UseCase の DI
def get_get_daily_nutrition_report_use_case() -> GetDailyNutritionReportUseCase:
    return GetDailyNutritionReportUseCase(
        uow=get_nutrition_uow(),
    )

# === MealRecommendation (今は Stub のみ) ====================================
# 食事レコメンド（将来の機能）の DI 定義


# 食事レコメンドを生成する Generator のシングルトンインスタンス
_recommendation_generator_singleton: MealRecommendationGeneratorPort | None = None


# 食事レコメンド生成ロジック（Stub）の実装を返す
def get_meal_recommendation_generator() -> MealRecommendationGeneratorPort:
    global _recommendation_generator_singleton
    if _recommendation_generator_singleton is None:
        _recommendation_generator_singleton = StubMealRecommendationGenerator()
    return _recommendation_generator_singleton


# ここから下は将来の実装用にコメントのまま残しておくイメージ
# def get_meal_recommendation_repository() -> MealRecommendationRepositoryPort:
#     session = get_db_session()
#     return SqlAlchemyMealRecommendationRepository(session)
#
#
# def get_generate_meal_recommendation_use_case() -> GenerateMealRecommendationUseCase:
#     session = get_db_session()
#
#     profile_repo: ProfileRepositoryPort = get_profile_repository(session=session)
#     target_repo: TargetRepositoryPort = SqlAlchemyTargetRepository(session)
#     daily_report_repo: DailyNutritionReportRepositoryPort = (
#         SqlAlchemyDailyNutritionReportRepository(session)
#     )
#     recommendation_repo: MealRecommendationRepositoryPort = (
#         SqlAlchemyMealRecommendationRepository(session)
#     )
#     generator: MealRecommendationGeneratorPort = get_meal_recommendation_generator()
#     clock: ClockPort = get_clock()
#
#     return GenerateMealRecommendationUseCase(
#         profile_repo=profile_repo,
#         target_repo=target_repo,
#         daily_report_repo=daily_report_repo,
#         recommendation_repo=recommendation_repo,
#         generator=generator,
#         clock=clock,
#         required_days=5,
#     )
