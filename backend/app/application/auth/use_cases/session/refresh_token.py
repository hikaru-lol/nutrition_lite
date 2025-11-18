from app.application.auth.dto.refresh_dto import RefreshInputDTO, RefreshOutputDTO
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.auth.ports.token_service_port import TokenServicePort, TokenPayload, TokenPair
from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.domain.auth.value_objects import UserId
from app.domain.auth.errors import InvalidRefreshTokenError, UserNotFoundError


class RefreshTokenUseCase:
    def __init__(
        self,
        token_service: TokenServicePort,
        user_repo: UserRepositoryPort,
    ) -> None:
        self._token_service = token_service
        self._user_repo = user_repo

    def execute(self, input_dto: RefreshInputDTO) -> RefreshOutputDTO:
        # refresh token 検証
        try:
            payload = self._token_service.verify_refresh_token(
                input_dto.refresh_token)
        except Exception:
            # TokenService 側で細かい例外を分けていても、UseCase 上では 1 種類にまとめる
            raise InvalidRefreshTokenError("Invalid or expired refresh token.")

        user = self._user_repo.get_by_id(UserId(payload.user_id))
        if user is None or not user.is_active:
            raise UserNotFoundError("User not found.")

        new_payload = TokenPayload(user_id=user.id.value, plan=user.plan)
        tokens: TokenPair = self._token_service.issue_tokens(new_payload)

        return RefreshOutputDTO(
            user=AuthUserDTO.from_entity(user),
            tokens=tokens,
        )
