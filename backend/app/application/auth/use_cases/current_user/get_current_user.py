from __future__ import annotations

from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.domain.auth.value_objects import UserId


class UserNotFoundError(Exception):
    pass


class GetCurrentUserUseCase:
    def __init__(self, user_repo: UserRepositoryPort) -> None:
        self._user_repo = user_repo

    def execute(self, user_id: str) -> AuthUserDTO:
        user = self._user_repo.get_by_id(UserId(user_id))
        if user is None or not user.is_active:
            raise UserNotFoundError("User not found")
        return AuthUserDTO.from_entity(user)
