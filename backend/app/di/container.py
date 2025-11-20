from __future__ import annotations

from sqlalchemy.orm import Session

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
from app.application.profile.use_cases.upsert_profile import UpsertProfileUseCase
from app.application.profile.use_cases.get_my_profile import GetMyProfileUseCase
from app.infra.db.uow import SqlAlchemyProfileUnitOfWork
from app.infra.storage.profile_image_storage import InMemoryProfileImageStorage


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


def get_get_current_user_use_case() -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(
        uow=get_auth_uow(),
    )


# --- Profile DI ----------------------------------------------------


# InMemory ストレージはプロセス内で共有したいので、シングルトン的に1インスタンスを持つ
_profile_image_storage_instance: InMemoryProfileImageStorage | None = None


def get_profile_image_storage() -> ProfileImageStoragePort:
    global _profile_image_storage_instance
    if _profile_image_storage_instance is None:
        _profile_image_storage_instance = InMemoryProfileImageStorage()
    return _profile_image_storage_instance


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
