from __future__ import annotations

from app.application.target.dto.target_dto import TargetDTO
from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.target import errors as target_errors


class GetActiveTargetUseCase:
    """
    現在アクティブなターゲットを取得するユースケース。

    - ユーザーにアクティブなターゲットが存在しない場合は NoActiveTargetError を投げる。
    """

    def __init__(self, uow: TargetUnitOfWorkPort) -> None:
        self._uow = uow

    def execute(self, user_id: str) -> TargetDTO:
        user_id_vo = UserId(user_id)

        with self._uow as uow:
            target = uow.target_repo.get_active_for_user(user_id_vo)
            if target is None:
                raise target_errors.NoActiveTargetError(
                    "Active target not found.")

        return TargetDTO.from_entity(target)
