from __future__ import annotations

from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.application.auth.ports.clock_port import ClockPort
from app.domain.auth.value_objects import UserId
from app.application.auth.use_cases.current_user.get_current_user import (
    UserNotFoundError,
)


class DeleteAccountUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        clock: ClockPort,
    ) -> None:
        self._user_repo = user_repo
        self._clock = clock

    def execute(self, user_id: str) -> None:
        user = self._user_repo.get_by_id(UserId(user_id))
        if user is None or not user.is_active:
            raise UserNotFoundError("User not found")

        user.mark_deleted(self._clock.now())
        self._user_repo.save(user)
