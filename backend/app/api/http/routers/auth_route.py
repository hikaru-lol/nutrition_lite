from __future__ import annotations

# === Standard library =======================================================
import logging

# === Third-party ============================================================
from fastapi import APIRouter, Cookie, Depends, Response, status

# === Auth (API 層) ==========================================================
from app.api.http.cookies import clear_auth_cookies, set_auth_cookies
from app.api.http.dependencies.auth import get_current_user_dto
from app.api.http.mappers.auth import to_user_summary
from app.api.http.schemas.auth import (
    AuthUserResponse,
    LoginRequest,
    RefreshResponse,
    RegisterRequest,
)
from app.api.http.schemas.errors import ErrorResponse

# === Auth (Application 層 DTO / UseCase) ====================================
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.auth.dto.login_dto import LoginInputDTO, LoginOutputDTO
from app.application.auth.dto.refresh_dto import RefreshInputDTO, RefreshOutputDTO
from app.application.auth.dto.register_dto import RegisterInputDTO, RegisterOutputDTO
from app.application.auth.use_cases.account.delete_account import DeleteAccountUseCase
from app.application.auth.use_cases.account.register_user import RegisterUserUseCase
from app.application.auth.use_cases.session.login_user import LoginUserUseCase
from app.application.auth.use_cases.session.logout_user import LogoutUserUseCase
from app.application.auth.use_cases.session.refresh_token import RefreshTokenUseCase

# === DI =====================================================================
from app.di.container import (
    get_delete_account_use_case,
    get_login_user_use_case,
    get_logout_user_use_case,
    get_refresh_token_use_case,
    get_register_user_use_case,
)


router = APIRouter(prefix="/auth", tags=["Auth"])

logger = logging.getLogger("auth_route")


# === Account ================================================================


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthUserResponse,
    responses={
        400: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def register(
    request: RegisterRequest,
    response: Response,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
) -> AuthUserResponse:
    """
    新規ユーザー登録 + ログイン（アクセストークン / リフレッシュトークン発行）。
    """
    input_dto = RegisterInputDTO(
        email=request.email,
        password=request.password,
        name=request.name,
    )

    result: RegisterOutputDTO = use_case.execute(input_dto)

    set_auth_cookies(response, result.tokens)
    return AuthUserResponse(user=to_user_summary(result.user))


@router.get(
    "/me",
    response_model=AuthUserResponse,
    responses={401: {"model": ErrorResponse}},
)
def get_me(
    current_user: AuthUserDTO = Depends(get_current_user_dto),
) -> AuthUserResponse:
    """
    現在ログイン中のユーザー情報を返す。
    """
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
    """
    自分のアカウントを削除して、セッション情報を破棄する。
    """
    use_case.execute(current_user.id)
    clear_auth_cookies(response)
    return None


# === Session ================================================================


@router.post(
    "/login",
    response_model=AuthUserResponse,
    responses={
        400: {"model": ErrorResponse},  # 入力バリデーション
        401: {"model": ErrorResponse},  # INVALID_CREDENTIALS など
    },
)
def login(
    request: LoginRequest,
    response: Response,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case),
) -> AuthUserResponse:
    """
    ログインしてアクセストークン / リフレッシュトークンを発行する。
    """
    input_dto = LoginInputDTO(email=request.email, password=request.password)
    output: LoginOutputDTO = use_case.execute(input_dto)

    logger.info("Login success: user_id=%s email=%s",
                output.user.id, output.user.email)

    set_auth_cookies(response, output.tokens)
    return AuthUserResponse(user=to_user_summary(output.user))


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    responses={
        401: {"model": ErrorResponse},
    },
)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias="REFRESH_TOKEN"),
    use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
) -> RefreshResponse:
    """
    リフレッシュトークンから新しいトークンペアを発行する。
    """
    from app.domain.auth.errors import InvalidRefreshTokenError  # 上に移動してもOK

    if refresh_token is None:
        # Cookie 自体がない場合は InvalidRefreshToken として扱う
        raise InvalidRefreshTokenError("Refresh token is missing.")

    output: RefreshOutputDTO = use_case.execute(
        RefreshInputDTO(refresh_token=refresh_token)
    )

    set_auth_cookies(response, output.tokens)
    return RefreshResponse(ok=True, user=to_user_summary(output.user))


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
    """
    ログアウト（サーバ側でのセッション破棄があればここで行う）。
    """
    use_case.execute(current_user.id)
    clear_auth_cookies(response)
    return None
