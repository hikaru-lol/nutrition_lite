from __future__ import annotations

from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.auth.dto.login_dto import LoginInputDTO, LoginOutputDTO

from app.application.auth.ports.uow_port import AuthUnitOfWorkPort
from app.application.auth.ports.password_hasher_port import PasswordHasherPort
from app.application.auth.ports.token_service_port import TokenServicePort, TokenPayload

from app.domain.auth.value_objects import EmailAddress
from app.domain.auth.errors import InvalidCredentialsError


class LoginUserUseCase:
    def __init__(
        self,
        uow: AuthUnitOfWorkPort,
        password_hasher: PasswordHasherPort,
        token_service: TokenServicePort,
    ) -> None:
        self._uow = uow
        self._password_hasher = password_hasher
        self._token_service = token_service

    def execute(self, input_dto: LoginInputDTO) -> LoginOutputDTO:
        email_vo = EmailAddress(input_dto.email)

        with self._uow as uow:
            user = uow.user_repo.get_by_email(email_vo)

            if user is None or not user.is_active:
                raise InvalidCredentialsError("Invalid email or password.")

            if not self._password_hasher.verify(input_dto.password, user.hashed_password):
                raise InvalidCredentialsError("Invalid email or password.")

        payload = TokenPayload(user_id=user.id.value, plan=user.plan)
        tokens = self._token_service.issue_tokens(payload)

        return LoginOutputDTO(
            user=AuthUserDTO.from_entity(user),
            tokens=tokens,
        )
