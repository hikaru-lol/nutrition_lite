from __future__ import annotations

import os
from sqlalchemy.orm import Session

from app.settings import settings

# --- auth 用 imports はそのまま ---
from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.application.auth.ports.password_hasher_port import PasswordHasherPort
from app.application.auth.ports.token_service_port import TokenServicePort
from app.application.auth.ports.clock_port import ClockPort
from app.application.auth.ports.uow_port import AuthUnitOfWorkPort

from app.application.auth.use_cases.account.register_user import RegisterUserUseCase
from app.application.auth.use_cases.session.login_user import LoginUserUseCase
from app.application.auth.use_cases.session.logout_user import LogoutUserUseCase
from app.application.auth.use_cases.session.refresh_token import RefreshTokenUseCase
from app.application.auth.use_cases.account.delete_account import DeleteAccountUseCase
from app.application.auth.use_cases.current_user.get_current_user import GetCurrentUserUseCase

from app.infra.db.session import create_session
from app.infra.db.repositories.user_repository import SqlAlchemyUserRepository
from app.infra.security.password_hasher import BcryptPasswordHasher
from app.infra.security.jwt_token_service import JwtTokenService
from app.infra.time.system_clock import SystemClock
from app.infra.db.uow import SqlAlchemyAuthUnitOfWork

# --- ★ profile 用 imports を追加 ---
from app.application.profile.ports.uow_port import ProfileUnitOfWorkPort
from app.application.profile.ports.profile_image_storage_port import ProfileImageStoragePort
from app.application.profile.ports.profile_repository_port import ProfileRepositoryPort
from app.application.profile.use_cases.upsert_profile import UpsertProfileUseCase
from app.application.profile.use_cases.get_my_profile import GetMyProfileUseCase
from app.infra.db.uow import SqlAlchemyProfileUnitOfWork
from app.infra.storage.profile_image_storage import InMemoryProfileImageStorage
from app.infra.storage.minio_profile_image_storage import MinioProfileImageStorage
from app.infra.profile.profile_query_service import ProfileQueryService
from app.application.profile.use_cases.get_my_profile import GetMyProfileUseCase
from app.infra.profile.profile_query_service import ProfileQueryService

# ★ Target 用の追加
from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.application.target.ports.target_generator_port import TargetGeneratorPort
from app.application.target.use_cases.create_target import CreateTargetUseCase
from app.application.target.use_cases.update_target import UpdateTargetUseCase
from app.application.target.use_cases.list_targets import ListTargetsUseCase
from app.application.target.use_cases.activate_target import ActivateTargetUseCase
from app.application.target.use_cases.get_active_target import GetActiveTargetUseCase
from app.application.target.use_cases.get_target import GetTargetUseCase
from app.infra.db.uow import SqlAlchemyTargetUnitOfWork
from app.infra.db.repositories.target_repository import SqlAlchemyTargetRepository
from app.infra.llm.target_generator_stub import StubTargetGenerator

# TargetGeneratorPortの実装
from app.application.target.ports.target_generator_port import TargetGeneratorPort
from app.infra.llm.target_generator_stub import StubTargetGenerator
from app.infra.llm.target_generator_openai import OpenAITargetGenerator, OpenAITargetGeneratorConfig

# --- Meal 用の imports を追加 ---
from app.application.meal.ports.food_entry_repository_port import FoodEntryRepositoryPort
from app.application.meal.use_cases.create_food_entry import CreateFoodEntryUseCase
from app.application.meal.use_cases.update_food_entry import UpdateFoodEntryUseCase
from app.application.meal.use_cases.delete_food_entry import DeleteFoodEntryUseCase
from app.application.meal.use_cases.list_food_entries_by_date import ListFoodEntriesByDateUseCase
from app.infra.db.repositories.food_entry_repository import SqlAlchemyFoodEntryRepository


def get_auth_uow() -> AuthUnitOfWorkPort:
    return SqlAlchemyAuthUnitOfWork()

# --- Ports ----------------------------------------------------


def get_db_session() -> Session:
    # NOTE: FastAPI から直接使うなら infra/db/session.get_db_session を Depends で
    #       コンテナ経由ならここで create_session を呼んで返す
    return create_session()


def get_user_repository() -> UserRepositoryPort:
    session = get_db_session()
    return SqlAlchemyUserRepository(session)


def get_password_hasher() -> PasswordHasherPort:
    return BcryptPasswordHasher()


def get_token_service() -> TokenServicePort:
    return JwtTokenService()


def get_clock() -> ClockPort:
    return SystemClock()


def get_profile_repository() -> ProfileRepositoryPort:
    session = get_db_session()
    return SqlAlchemyTargetRepository(session)

# --- Auth UseCases --------------------------------------------------


def get_register_user_use_case() -> RegisterUserUseCase:
    return RegisterUserUseCase(
        uow=get_auth_uow(),
        password_hasher=get_password_hasher(),
        token_service=get_token_service(),
        clock=get_clock(),
    )


def get_login_user_use_case() -> LoginUserUseCase:
    return LoginUserUseCase(
        uow=get_auth_uow(),
        password_hasher=get_password_hasher(),
        token_service=get_token_service(),
    )


def get_logout_user_use_case() -> LogoutUserUseCase:
    return LogoutUserUseCase()


def get_delete_account_use_case() -> DeleteAccountUseCase:
    return DeleteAccountUseCase(
        uow=get_auth_uow(),
        clock=get_clock(),
    )


def get_refresh_token_use_case() -> RefreshTokenUseCase:
    return RefreshTokenUseCase(
        uow=get_auth_uow(),
        token_service=get_token_service(),
    )


def get_current_user_use_case() -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(
        uow=get_auth_uow(),
    )


# --- Profile DI ----------------------------------------------------


# InMemory ストレージはプロセス内で共有したいので、シングルトン的に1インスタンスを持つ
_profile_image_storage_instance: InMemoryProfileImageStorage | None = None
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


def get_upsert_profile_use_case() -> UpsertProfileUseCase:
    return UpsertProfileUseCase(
        uow=get_profile_uow(),
        image_storage=get_profile_image_storage(),
    )


def get_get_my_profile_use_case() -> GetMyProfileUseCase:
    return GetMyProfileUseCase(
        uow=get_profile_uow(),
    )


# --- Target 用のUoW / Generator -------------------------------------


def get_target_uow() -> TargetUnitOfWorkPort:
    return SqlAlchemyTargetUnitOfWork()


# Target生成ロジック（Stub）。後で本番用の実装に差し替え可能。
_target_generator_singleton: TargetGeneratorPort | None = None

_USE_OPENAI_TARGET_GENERATOR = os.getenv("USE_OPENAI_TARGET_GENERATOR", "false").lower() in (
    "1", "true", "yes", "on"
)


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


def get_profile_query_service() -> ProfileQueryService:
    return ProfileQueryService(
        get_my_profile_uc=get_get_my_profile_use_case(),
    )


def get_create_target_use_case() -> CreateTargetUseCase:
    """
    /target/create のための UseCase をDIする。
    """
    return CreateTargetUseCase(
        uow=get_target_uow(),
        profile_repo=get_profile_repository(),
        generator=get_target_generator(),
        profile_query=get_profile_query_service(),
    )


def get_get_active_target_use_case() -> GetMyProfileUseCase:
    """
    /target/active（現在のターゲット取得）のための UseCase。
    """
    return GetActiveTargetUseCase(
        uow=get_target_uow(),
    )


def get_list_targets_use_case() -> ListTargetsUseCase:
    """
    /target/list のための UseCase。
    """
    return ListTargetsUseCase(
        uow=get_target_uow(),
    )


def get_activate_target_use_case() -> ActivateTargetUseCase:
    """
    /target/activate のための UseCase。
    """
    return ActivateTargetUseCase(
        uow=get_target_uow(),
        clock=get_clock(),
    )


def get_update_target_use_case() -> UpdateTargetUseCase:
    """
    /target/update のための UseCase。
    """
    return UpdateTargetUseCase(
        uow=get_target_uow(),
        clock=get_clock(),
    )


def get_get_target_use_case() -> GetTargetUseCase:
    """
    /target/get のための UseCase。
    """
    return GetTargetUseCase(
        uow=get_target_uow(),
    )

# --- Meal 用のUoW / Repository -------------------------------------


# def get_meal_uow() -> MealUnitOfWorkPort:
#     return SqlAlchemyMealUnitOfWork()


def get_food_entry_repository() -> FoodEntryRepositoryPort:
    session = get_db_session()
    return SqlAlchemyFoodEntryRepository(session)


# --- Meal UseCases ----------------------------------------------------

def get_create_food_entry_use_case() -> CreateFoodEntryUseCase:
    return CreateFoodEntryUseCase(
        food_entry_repository=get_food_entry_repository(),
    )


def get_update_food_entry_use_case() -> UpdateFoodEntryUseCase:
    return UpdateFoodEntryUseCase(
        food_entry_repository=get_food_entry_repository(),
    )


def get_delete_food_entry_use_case() -> DeleteFoodEntryUseCase:
    return DeleteFoodEntryUseCase(
        food_entry_repository=get_food_entry_repository(),
    )


def get_list_food_entries_by_date_use_case() -> ListFoodEntriesByDateUseCase:
    return ListFoodEntriesByDateUseCase(
        food_entry_repository=get_food_entry_repository(),
    )
