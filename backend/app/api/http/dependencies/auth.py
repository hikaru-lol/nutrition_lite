from __future__ import annotations

from fastapi import Depends, Cookie, HTTPException, status

from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.auth.use_cases.current_user.get_current_user import (
    GetCurrentUserUseCase,
    UserNotFoundError,
)
from app.application.auth.ports.token_service_port import TokenServicePort
from app.infra.security.jwt_token_service import InvalidTokenError
from app.di.container import get_get_current_user_use_case, get_token_service


def get_current_user_dto(
    access_token: str | None = Cookie(default=None, alias="ACCESS_TOKEN"),
    token_service: TokenServicePort = Depends(get_token_service),
    use_case: GetCurrentUserUseCase = Depends(get_get_current_user_use_case),
) -> AuthUserDTO:
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = token_service.verify_access_token(access_token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    try:
        dto = use_case.execute(payload.user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return dto
