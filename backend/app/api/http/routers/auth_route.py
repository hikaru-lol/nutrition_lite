from __future__ import annotations

from fastapi import APIRouter, Depends, Response, HTTPException, status

from app.api.http.dependencies.auth import get_current_user_dto
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.auth.ports.token_service_port import TokenPair


from app.api.http.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    AuthUserResponse,
    ErrorResponse,
    UserSummary,
)
from app.application.auth.dto.register_dto import RegisterInputDTO
from app.application.auth.dto.login_dto import LoginInputDTO
from app.application.auth.use_cases.account.register_user import (
    RegisterUserUseCase,
    EmailAlreadyUsedError,
)
from app.application.auth.use_cases.session.login_user import (
    LoginUserUseCase,
    InvalidCredentialsError,
)
from app.di.container import get_register_user_use_case, get_login_user_use_case


router = APIRouter(prefix="/auth", tags=["Auth"])


def set_auth_cookies(response: Response, tokens: TokenPair) -> None:
    # 実運用では secure / samesite 等も設定
    response.set_cookie(
        key="ACCESS_TOKEN",
        value=tokens.access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        key="REFRESH_TOKEN",
        value=tokens.refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    for key in ("ACCESS_TOKEN", "REFRESH_TOKEN"):
        response.set_cookie(
            key=key,
            value="",
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
            max_age=0,
        )


def to_user_summary(dto: AuthUserDTO) -> UserSummary:
    return UserSummary(
        id=dto.id,
        email=dto.email,
        name=dto.name,
        plan=dto.plan.value,
        trialEndsAt=dto.trial_ends_at,
        hasProfile=dto.has_profile,
        createdAt=dto.created_at,
    )


@router.post(
    "/register",
    response_model=AuthUserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}},
)
def register(
    request: RegisterRequest,
    response: Response,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
) -> AuthUserResponse:
    input_dto = RegisterInputDTO(
        email=request.email,
        password=request.password,
        name=request.name,
    )
    try:
        output = use_case.execute(input_dto)
    except EmailAlreadyUsedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    set_auth_cookies(response, output.tokens)
    return AuthUserResponse(user=to_user_summary(output.user))


@router.post(
    "/login",
    response_model=AuthUserResponse,
    responses={401: {"model": ErrorResponse}},
)
def login(
    request: LoginRequest,
    response: Response,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case),
) -> AuthUserResponse:
    input_dto = LoginInputDTO(email=request.email, password=request.password)
    try:
        output = use_case.execute(input_dto)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    set_auth_cookies(response, output.tokens)
    return AuthUserResponse(user=to_user_summary(output.user))


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(response: Response) -> None:
    # トークンをサーバ側で無効化する仕組みを入れるなら、ここで UseCase を呼ぶ
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
