from __future__ import annotations

from sqlalchemy.orm import Session

from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.application.auth.ports.password_hasher_port import PasswordHasherPort
from app.application.auth.ports.token_service_port import TokenServicePort
from app.application.auth.ports.clock_port import ClockPort

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


# --- UseCase --------------------------------------------------


def get_register_user_use_case() -> RegisterUserUseCase:
    return RegisterUserUseCase(
        user_repo=get_user_repository(),
        password_hasher=get_password_hasher(),
        token_service=get_token_service(),
        clock=get_clock(),
    )


def get_login_user_use_case() -> LoginUserUseCase:
    return LoginUserUseCase(
        user_repo=get_user_repository(),
        password_hasher=get_password_hasher(),
        token_service=get_token_service(),
    )


def get_logout_user_use_case() -> LogoutUserUseCase:
    return LogoutUserUseCase()


def get_delete_account_use_case() -> DeleteAccountUseCase:
    return DeleteAccountUseCase(
        user_repo=get_user_repository(),
        clock=get_clock(),
    )


def get_refresh_token_use_case() -> RefreshTokenUseCase:
    return RefreshTokenUseCase(
        token_service=get_token_service(),
        user_repo=get_user_repository(),
    )


def get_get_current_user_use_case() -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(
        user_repo=get_user_repository(),
    )
