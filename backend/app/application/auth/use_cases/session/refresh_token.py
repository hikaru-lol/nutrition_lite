from __future__ import annotations

from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.auth.dto.refresh_dto import RefreshInputDTO, RefreshOutputDTO

from app.application.auth.ports.uow_port import AuthUnitOfWorkPort
from app.application.auth.ports.token_service_port import TokenServicePort, TokenPayload, TokenPair

from app.domain.auth.value_objects import UserId
from app.domain.auth.errors import InvalidRefreshTokenError, UserNotFoundError


class RefreshTokenUseCase:
    def __init__(
        self,
        uow: AuthUnitOfWorkPort,
        token_service: TokenServicePort,
    ) -> None:
        self._uow = uow
        self._token_service = token_service

    def execute(self, input_dto: RefreshInputDTO) -> RefreshOutputDTO:
        try:
            payload = self._token_service.verify_refresh_token(
                input_dto.refresh_token)
        except Exception:
            raise InvalidRefreshTokenError("Invalid or expired refresh token.")

        with self._uow as uow:
            user = uow.user_repo.get_by_id(UserId(payload.user_id))
            if user is None or not user.is_active:
                raise UserNotFoundError("User not found.")

        new_payload = TokenPayload(user_id=user.id.value, plan=user.plan)
        tokens: TokenPair = self._token_service.issue_tokens(new_payload)

        return RefreshOutputDTO(
            user=AuthUserDTO.from_entity(user),
            tokens=tokens,
        )
