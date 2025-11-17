from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.application.auth.ports.password_hasher_port import PasswordHasherPort
from app.application.auth.ports.token_service_port import TokenServicePort
from app.application.auth.ports.clock_port import ClockPort

from app.application.auth.use_cases.account.register_user import RegisterUserUseCase
from app.application.auth.use_cases.account.delete_account import DeleteAccountUseCase
from app.application.auth.use_cases.session.login_user import LoginUserUseCase
from app.application.auth.use_cases.session.logout_user import LogoutUserUseCase
from app.application.auth.use_cases.session.refresh_token import RefreshTokenUseCase
from app.application.auth.use_cases.current_user.get_current_user import GetCurrentUserUseCase

from app.infra.db.base import get_db
from app.infra.db.repositories.user_repository import SqlAlchemyUserRepository
from app.infra.security.password_hasher import BcryptPasswordHasher
from app.infra.security.jwt_token_service import JwtTokenService
from app.infra.time.system_clock import SystemClock


# --- Port 実装の DI ---


def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryPort:
    return SqlAlchemyUserRepository(db)


def get_password_hasher() -> PasswordHasherPort:
    return BcryptPasswordHasher()


def get_token_service() -> TokenServicePort:
    return JwtTokenService()


def get_clock() -> ClockPort:
    return SystemClock()


# --- UseCase の DI ---


def get_register_user_use_case(
    user_repo: UserRepositoryPort = Depends(get_user_repository),
    password_hasher: PasswordHasherPort = Depends(get_password_hasher),
    token_service: TokenServicePort = Depends(get_token_service),
    clock: ClockPort = Depends(get_clock),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(
        user_repo=user_repo,
        password_hasher=password_hasher,
        token_service=token_service,
        clock=clock,
    )


def get_login_user_use_case(
    user_repo: UserRepositoryPort = Depends(get_user_repository),
    password_hasher: PasswordHasherPort = Depends(get_password_hasher),
    token_service: TokenServicePort = Depends(get_token_service),
) -> LoginUserUseCase:
    return LoginUserUseCase(
        user_repo=user_repo,
        password_hasher=password_hasher,
        token_service=token_service,
    )


def get_get_current_user_use_case(
    user_repo: UserRepositoryPort = Depends(get_user_repository),
) -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(user_repo=user_repo)


def get_refresh_token_use_case(
    user_repo: UserRepositoryPort = Depends(get_user_repository),
    token_service: TokenServicePort = Depends(get_token_service),
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(
        user_repo=user_repo,
        token_service=token_service,
    )


def get_logout_user_use_case() -> LogoutUserUseCase:
    return LogoutUserUseCase()


def get_delete_account_use_case(
    user_repo: UserRepositoryPort = Depends(get_user_repository),
    clock: ClockPort = Depends(get_clock),
) -> DeleteAccountUseCase:
    return DeleteAccountUseCase(
        user_repo=user_repo,
        clock=clock,
    )
