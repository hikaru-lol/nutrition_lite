from __future__ import annotations

from fastapi import Cookie, Depends

from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.auth.ports.token_service_port import TokenServicePort
from app.application.auth.use_cases.current_user.get_current_user import (
    GetCurrentUserUseCase,
)

from app.di.container import get_current_user_use_case, get_token_service

from app.domain.auth.errors import InvalidCredentialsError


def get_current_user_dto(
    access_token: str | None = Cookie(default=None, alias="ACCESS_TOKEN"),
    token_service: TokenServicePort = Depends(get_token_service),
    use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
) -> AuthUserDTO:
    if access_token is None:
        # 認証エラーをドメインエラーとして投げる
        raise InvalidCredentialsError("Access token is missing.")

    payload = token_service.verify_access_token(access_token)
    # payload.user_id から現在のユーザーを取得（見つからなければ UserNotFoundError）
    return use_case.execute(payload.user_id)
