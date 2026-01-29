from __future__ import annotations

from app.application.target.dto.target_dto import DeleteTargetInputDTO
from app.application.target.errors import TargetNotFoundError
from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.target.value_objects import TargetId


class DeleteTargetUseCase:
    """
    指定した TargetDefinition を削除するユースケース。

    - user_id + target_id で検索し、存在しなければ TargetNotFoundError
    - 削除成功時は None を返す（204 No Content 想定）
    """

    def __init__(self, uow: TargetUnitOfWorkPort) -> None:
        self._uow = uow

    def execute(self, input_dto: DeleteTargetInputDTO) -> None:
        user_id = UserId(input_dto.user_id)
        target_id = TargetId(input_dto.target_id)

        with self._uow as uow:
            deleted = uow.target_repo.delete(
                user_id=user_id, target_id=target_id)
            if not deleted:
                raise TargetNotFoundError(
                    "Target not found or does not belong to the current user."
                )
            uow.commit()
