from __future__ import annotations

from app.application.auth.ports.uow_port import AuthUnitOfWorkPort
from app.application.auth.ports.clock_port import ClockPort

from app.domain.auth.value_objects import UserId
from app.domain.auth.errors import UserNotFoundError


class DeleteAccountUseCase:
    def __init__(
        self,
        uow: AuthUnitOfWorkPort,
        clock: ClockPort,
    ) -> None:
        self._uow = uow
        self._clock = clock

    def execute(self, user_id: str) -> None:
        with self._uow as uow:
            user = uow.user_repo.get_by_id(UserId(user_id))
            if user is None:
                raise UserNotFoundError("User not found.")

            now = self._clock.now()
            user.mark_deleted(now)
            uow.user_repo.save(user)
