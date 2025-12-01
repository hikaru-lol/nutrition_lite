from __future__ import annotations

from app.application.target.dto.target_dto import (
    GetActiveTargetInputDTO,
    TargetDTO,
    TargetNutrientDTO,
)

from app.application.target.ports.uow_port import TargetUnitOfWorkPort

from app.application.target.errors import TargetNotFoundError

from app.domain.auth.value_objects import UserId
from app.domain.target.entities import TargetDefinition


class GetActiveTargetUseCase:
    """
    現在 Active な TargetDefinition を 1件取得するユースケース。

    - 該当ターゲットがない場合は TargetNotFoundError を送出する。
    """

    def __init__(self, uow: TargetUnitOfWorkPort) -> None:
        self._uow = uow

    def execute(self, input_dto: GetActiveTargetInputDTO) -> TargetDTO:
        user_id = UserId(input_dto.user_id)
        with self._uow as uow:
            target = uow.target_repo.get_active(user_id)
            if target is None:
                raise TargetNotFoundError(
                    "Active target not found for the current user."
                )
            return _to_dto(target)


def _to_dto(target: TargetDefinition) -> TargetDTO:
    nutrients_dto = [
        TargetNutrientDTO(
            code=n.code.value,
            amount=n.amount.value,
            unit=n.amount.unit,
            source=n.source.value,
        )
        for n in target.nutrients
    ]

    return TargetDTO(
        id=target.id.value,
        user_id=target.user_id.value,
        title=target.title,
        goal_type=target.goal_type.value,
        goal_description=target.goal_description,
        activity_level=target.activity_level.value,
        is_active=target.is_active,
        nutrients=nutrients_dto,
        llm_rationale=target.llm_rationale,
        disclaimer=target.disclaimer,
        created_at=target.created_at,
        updated_at=target.updated_at,
    )
