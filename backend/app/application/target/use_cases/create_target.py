from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

# === Application (DTO / Ports) ==============================================

from app.application.profile.ports.profile_query_port import (
    ProfileForTarget,
    ProfileQueryPort,
)
from app.application.auth.ports.clock_port import ClockPort
from app.application.target.dto.target_dto import (
    CreateTargetInputDTO,
    TargetDTO,
    TargetNutrientDTO,
)
from app.application.target.errors import TargetLimitExceededError
from app.application.target.ports.target_generator_port import (
    TargetGenerationContext,
    TargetGeneratorPort,
)
from app.application.target.ports.uow_port import TargetUnitOfWorkPort

# === Domain (Entities / ValueObjects / Errors) ==============================

from app.domain.auth.value_objects import UserId
from app.domain.profile.errors import ProfileNotFoundError
from app.domain.target.entities import TargetDefinition
from app.domain.target.value_objects import ActivityLevel, GoalType, TargetId, ALL_NUTRIENT_CODES

MAX_TARGETS_PER_USER = 5


class CreateTargetUseCase:
    """
    新しい TargetDefinition を作成するユースケース。

    - プロフィール + 目標情報から TargetGeneratorPort を使って 10 栄養素を生成
    - 初めての Target なら is_active=True、それ以外は is_active=False
    """

    def __init__(
        self,
        uow: TargetUnitOfWorkPort,
        generator: TargetGeneratorPort,
        profile_query: ProfileQueryPort,
        clock: ClockPort,
    ) -> None:
        self._uow = uow
        self._generator = generator
        self._profile_query = profile_query
        self._clock = clock

    def execute(self, input_dto: CreateTargetInputDTO) -> TargetDTO:
        """
        ターゲットを 1 件生成して永続化し、TargetDTO として返す。

        Raises:
            TargetLimitExceededError: ユーザーが既に上限数のターゲットを持っている場合
            ProfileNotFoundError: ターゲット生成に必要なプロフィールが存在しない場合
        """
        user_id = UserId(input_dto.user_id)

        with self._uow as uow:
            # --- 1. 上限チェック（5個まで） ---------------------------
            existing_targets = uow.target_repo.list_by_user(
                user_id=user_id,
                limit=MAX_TARGETS_PER_USER + 1,
            )
            if len(existing_targets) >= MAX_TARGETS_PER_USER:
                raise TargetLimitExceededError(
                    f"User already has {MAX_TARGETS_PER_USER} targets."
                )

            # --- 2. プロフィール取得 -----------------------------------
            profile: ProfileForTarget | None = self._profile_query.get_profile_for_target(
                user_id
            )
            if profile is None:
                raise ProfileNotFoundError(
                    f"Profile not found for user {user_id}."
                )

            # --- 3. ターゲット生成（LLM or Stub） ----------------------
            ctx = TargetGenerationContext(
                user_id=user_id,
                sex=profile.sex,
                birthdate=profile.birthdate,
                height_cm=profile.height_cm,
                weight_kg=profile.weight_kg,
                goal_type=GoalType(input_dto.goal_type),
                activity_level=ActivityLevel(input_dto.activity_level),
            )
            gen_result = self._generator.generate(ctx)

            # ここで「10 栄養素そろっているか」を検査
            present = {n.code for n in gen_result.nutrients}
            missing = [
                code for code in ALL_NUTRIENT_CODES if code not in present]
            if missing:
                codes_str = ", ".join(c.value for c in missing)
                raise ValueError(
                    f"TargetGenerator returned nutrients missing codes: {codes_str}"
                )

            # 既にアクティブなターゲットがなければ、このターゲットを is_active=True に
            already_active = uow.target_repo.get_active(user_id)
            is_active = already_active is None

            # --- 4. TargetDefinition を組み立て -----------------------
            now = self._clock.now()
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

            return _to_dto(target)


# === Domain -> DTO 変換ヘルパー ============================================


def _to_dto(target: TargetDefinition) -> TargetDTO:
    """
    Domain の TargetDefinition -> Application 層の TargetDTO 変換。
    """
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
