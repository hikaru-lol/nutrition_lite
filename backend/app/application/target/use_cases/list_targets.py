from __future__ import annotations

from app.application.target.dto.target_dto import (
    ListTargetsInputDTO,
    TargetDTO,
    TargetNutrientDTO,
)
from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.target.entities import TargetDefinition


class ListTargetsUseCase:
    """
    ユーザーに紐づく TargetDefinition 一覧を取得するユースケース。

    - ページング (limit / offset) 対応
    - 並び順は Repository 実装側で決定（通常は created_at DESC が自然）
    """

    def __init__(self, uow: TargetUnitOfWorkPort) -> None:
        self._uow = uow

    def execute(self, input_dto: ListTargetsInputDTO) -> list[TargetDTO]:
        user_id = UserId(input_dto.user_id)
        with self._uow as uow:
            targets = uow.target_repo.list_by_user(
                user_id=user_id,
                limit=input_dto.limit,
                offset=input_dto.offset,
            )
            return [_to_dto(t) for t in targets]


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
