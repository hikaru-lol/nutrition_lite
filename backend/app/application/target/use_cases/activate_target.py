from __future__ import annotations

from datetime import datetime, timezone

from app.application.target.dto.target_dto import (
    ActivateTargetInputDTO,
    TargetDTO,
    TargetNutrientDTO,
)
from app.application.target.errors import TargetNotFoundError
from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.target.entities import TargetDefinition
from app.domain.target.value_objects import TargetId


class ActivateTargetUseCase:
    """
    指定した TargetDefinition を Active にするユースケース。

    - 同一ユーザーの他のターゲットはすべて is_active=False にする
    - 指定 ID のターゲットが見つからない場合は TargetNotFoundError
    """

    def __init__(self, uow: TargetUnitOfWorkPort) -> None:
        self._uow = uow

    def execute(self, input_dto: ActivateTargetInputDTO) -> TargetDTO:
        user_id = UserId(input_dto.user_id)
        target_id = TargetId(input_dto.target_id)

        with self._uow as uow:
            target = uow.target_repo.get_by_id(
                user_id=user_id, target_id=target_id)
            if target is None:
                raise TargetNotFoundError(
                    "Target not found or does not belong to the current user."
                )

            uow.target_repo.deactivate_all(user_id)
            target.set_active()
            target.update_timestamp(datetime.now(timezone.utc))

            uow.target_repo.save(target)
            uow.commit()

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
