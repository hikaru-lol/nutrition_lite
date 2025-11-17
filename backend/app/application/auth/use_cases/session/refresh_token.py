from __future__ import annotations

from dataclasses import dataclass

from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.application.auth.ports.token_service_port import (
    TokenServicePort,
    TokenPair,
    TokenPayload,
)
from app.domain.auth.value_objects import UserId
from app.application.auth.use_cases.current_user.get_current_user import (
    UserNotFoundError,
)


class InvalidRefreshTokenError(Exception):
    pass


@dataclass
class RefreshInputDTO:
    refresh_token: str


@dataclass
class RefreshOutputDTO:
    user: AuthUserDTO
    tokens: TokenPair


class RefreshTokenUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        token_service: TokenServicePort,
    ) -> None:
        self._user_repo = user_repo
        self._token_service = token_service

    def execute(self, input_dto: RefreshInputDTO) -> RefreshOutputDTO:
        try:
            payload: TokenPayload = self._token_service.verify_refresh_token(
                input_dto.refresh_token
            )
        except Exception as e:
            # TokenServicePort 実装側のエラーを丸めて扱う
            raise InvalidRefreshTokenError(
                "Invalid or expired refresh token") from e

        user = self._user_repo.get_by_id(UserId(payload.user_id))
        if user is None or not user.is_active:
            raise UserNotFoundError("User not found")

        # token 内の plan ではなく、DB 上の plan を信頼する
        new_payload = TokenPayload(user_id=user.id.value, plan=user.plan)
        new_tokens = self._token_service.issue_tokens(new_payload)

        return RefreshOutputDTO(
            user=AuthUserDTO.from_entity(user),
            tokens=new_tokens,
        )
