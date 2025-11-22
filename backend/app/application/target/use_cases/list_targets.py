from __future__ import annotations

from typing import List

from app.application.target.dto.target_dto import TargetDTO
from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.domain.auth.value_objects import UserId


class ListTargetsUseCase:
    """
    現在ユーザーが持つターゲット一覧（最大5件）を取得するユースケース。
    """

    def __init__(self, uow: TargetUnitOfWorkPort) -> None:
        self._uow = uow

    def execute(self, user_id: str) -> List[TargetDTO]:
        user_id_vo = UserId(user_id)

        with self._uow as uow:
            targets = uow.target_repo.list_for_user(user_id_vo)

        return [TargetDTO.from_entity(t) for t in targets]
