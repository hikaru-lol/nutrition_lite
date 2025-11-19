from __future__ import annotations

from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.auth.ports.uow_port import AuthUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.auth.errors import UserNotFoundError


class GetCurrentUserUseCase:
    def __init__(self, uow: AuthUnitOfWorkPort) -> None:
        self._uow = uow

    def execute(self, user_id: str) -> AuthUserDTO:
        with self._uow as uow:
            user = uow.user_repo.get_by_id(UserId(user_id))
            if user is None or not user.is_active:
                raise UserNotFoundError("User not found")

        return AuthUserDTO.from_entity(user)
