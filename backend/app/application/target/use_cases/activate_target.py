from __future__ import annotations

from app.application.auth.ports.clock_port import ClockPort
from app.application.target.dto.target_dto import ActivateTargetInputDTO, TargetDTO
from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.target import errors as target_errors
from app.domain.target.value_objects import TargetId


class ActivateTargetUseCase:
    """
    指定したターゲットをアクティブ化し、それ以外のターゲットをすべて非アクティブにするユースケース。

    - 1ユーザーにつき is_active=True なターゲットは高々 1 件になる。
    """

    def __init__(self, uow: TargetUnitOfWorkPort, clock: ClockPort) -> None:
        self._uow = uow
        self._clock = clock

    def execute(self, input_dto: ActivateTargetInputDTO) -> TargetDTO:
        user_id_vo = UserId(input_dto.user_id)
        target_id_vo = TargetId(input_dto.target_id)
        now = self._clock.now()

        with self._uow as uow:
            targets = uow.target_repo.list_for_user(user_id_vo)

            target_to_activate = None

            for t in targets:
                if t.id == target_id_vo:
                    target_to_activate = t

            if target_to_activate is None:
                raise target_errors.TargetNotFoundError("Target not found.")

            # 全ターゲットを走査して、アクティブ状態を調整
            for t in targets:
                if t.id == target_to_activate.id:
                    if not t.is_active:
                        t.set_active()
                        t.update_timestamp(now)
                        uow.target_repo.save(t)
                else:
                    if t.is_active:
                        t.set_inactive()
                        t.update_timestamp(now)
                        uow.target_repo.save(t)

            # 戻り値はアクティブにしたターゲット
            return TargetDTO.from_entity(target_to_activate)
