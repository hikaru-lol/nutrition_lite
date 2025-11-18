from __future__ import annotations

from fastapi import APIRouter, Depends, Response, HTTPException, status, Cookie
from dataclasses import dataclass

from app.api.http.dependencies.auth import get_current_user_dto
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.auth.ports.token_service_port import TokenPair
from app.application.auth.use_cases.session.logout_user import LogoutUserUseCase

from app.api.http.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshResponse,
    AuthUserResponse,
    ErrorResponse,
)

from app.api.http.mappers.auth import to_user_summary

from app.application.auth.dto.register_dto import RegisterInputDTO, RegisterOutputDTO
from app.application.auth.dto.login_dto import LoginInputDTO, LoginOutputDTO
from app.application.auth.use_cases.account.register_user import (
    RegisterUserUseCase,
)
from app.application.auth.use_cases.session.login_user import (
    LoginUserUseCase,
)
from app.application.auth.use_cases.session.refresh_token import (
    RefreshTokenUseCase,
    InvalidRefreshTokenError,
)
from app.application.auth.use_cases.account.delete_account import (
    DeleteAccountUseCase,
    UserNotFoundError,
)
from app.di.container import get_register_user_use_case, get_login_user_use_case
from app.di.container import get_logout_user_use_case, get_delete_account_use_case, get_refresh_token_use_case

from app.api.http.cookies import set_auth_cookies, clear_auth_cookies


router = APIRouter(prefix="/auth", tags=["Auth"])


class InvalidRefreshTokenError(Exception):
    pass


@dataclass
class RefreshInputDTO:
    refresh_token: str


@dataclass
class RefreshOutputDTO:
    user: AuthUserDTO
    tokens: TokenPair


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthUserResponse,
    responses={
        400: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def register(
    request: RegisterRequest,
    response: Response,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
):
    result: RegisterOutputDTO = await use_case.execute(RegisterInputDTO(
        email=request.email,
        password=request.password,
        name=request.name,
    ))

    set_auth_cookies(response, result.tokens)

    return AuthUserResponse(user=to_user_summary(result.user))


@router.post(
    "/login",
    response_model=AuthUserResponse,
    responses={
        400: {"model": ErrorResponse},  # バリデーションエラー用
        401: {"model": ErrorResponse},  # INVALID_CREDENTIALS
    },
)
def login(
    request: LoginRequest,
    response: Response,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case),
) -> AuthUserResponse:
    input_dto = LoginInputDTO(email=request.email, password=request.password)

    # ここで InvalidCredentialsError が発生したら、
    # → auth_error_handler が 401 + ErrorResponse に変換してくれる
    output: LoginOutputDTO = use_case.execute(input_dto)

    set_auth_cookies(response, output.tokens)
    return AuthUserResponse(user=to_user_summary(output.user))


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"model": ErrorResponse}},
)
def logout(
    response: Response,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: LogoutUserUseCase = Depends(get_logout_user_use_case),
) -> None:
    # 現時点では No-Op だが、将来的にサーバ側セッション無効化などをここに追加
    use_case.execute(current_user.id)
    clear_auth_cookies(response)
    return None


@router.get(
    "/me",
    response_model=AuthUserResponse,
    responses={401: {"model": ErrorResponse}},
)
def get_me(
    current_user: AuthUserDTO = Depends(get_current_user_dto),
) -> AuthUserResponse:
    return AuthUserResponse(user=to_user_summary(current_user))


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse},
    },
)
def delete_me(
    response: Response,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: DeleteAccountUseCase = Depends(get_delete_account_use_case),
) -> None:
    use_case.execute(current_user.id)
    clear_auth_cookies(response)
    return None


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    responses={401: {"model": ErrorResponse}},
)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias="REFRESH_TOKEN"),
    use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
) -> RefreshResponse:
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing",
        )

    try:
        output = use_case.execute(RefreshInputDTO(refresh_token=refresh_token))
    except InvalidRefreshTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    set_auth_cookies(response, output.tokens)
    return RefreshResponse(ok=True, user=to_user_summary(output.user))
