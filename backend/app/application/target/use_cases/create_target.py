from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.application.target.dto.target_dto import (
    CreateTargetInputDTO,
    TargetDTO,
    TargetNutrientDTO,
)
from app.application.target.errors import TargetLimitExceededError
from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.application.target.ports.target_generator_port import (
    TargetGeneratorPort,
    TargetGenerationContext,
)
from app.domain.auth.value_objects import UserId
from app.domain.target.entities import TargetDefinition
from app.domain.target.value_objects import (
    TargetId,
    GoalType,
    ActivityLevel,
)


MAX_TARGETS_PER_USER = 5


class CreateTargetUseCase:
    """
    新しい TargetDefinition を作成するユースケース。

    - プロフィール + 目標情報から TargetGeneratorPort を使って 17 栄養素を生成
    - 初めての Target なら is_active=True、それ以外は is_active=False
    - 将来的には Profile 情報を ctx に詰めて渡す想定（いまは未使用部分は None）
    """

    def __init__(
        self,
        uow: TargetUnitOfWorkPort,
        generator: TargetGeneratorPort,
    ) -> None:
        self._uow = uow
        self._generator = generator

    def execute(self, input_dto: CreateTargetInputDTO) -> TargetDTO:
        user_id = UserId(input_dto.user_id)

        with self._uow as uow:
            # --- 上限チェック（5個まで） ------------------------------
            existing_targets = uow.target_repo.list_by_user(
                user_id=user_id,
                limit=MAX_TARGETS_PER_USER + 1,
            )
            if len(existing_targets) >= MAX_TARGETS_PER_USER:
                raise TargetLimitExceededError(
                    f"User already has {MAX_TARGETS_PER_USER} targets."
                )

            # --- ターゲット生成（LLM or Stub） ------------------------
            ctx = TargetGenerationContext(
                user_id=user_id,
                sex=None,
                birthdate=None,
                height_cm=None,
                weight_kg=None,
                goal_type=GoalType(input_dto.goal_type),
                activity_level=ActivityLevel(input_dto.activity_level),
            )
            gen_result = self._generator.generate(ctx)

            already_active = uow.target_repo.get_active(user_id)
            is_active = already_active is None

            now = datetime.now(timezone.utc)
            target = TargetDefinition(
                id=TargetId(str(uuid4())),
                user_id=user_id,
                title=input_dto.title,
                goal_type=GoalType(input_dto.goal_type),
                goal_description=input_dto.goal_description,
                activity_level=ActivityLevel(input_dto.activity_level),
                nutrients=gen_result.nutrients,
                is_active=is_active,
                created_at=now,
                updated_at=now,
                llm_rationale=gen_result.llm_rationale,
                disclaimer=gen_result.disclaimer,
            )

            uow.target_repo.add(target)
            uow.commit()

            return _to_dto(target)


# --- Domain -> DTO 変換ヘルパー ----------------------------------------


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
