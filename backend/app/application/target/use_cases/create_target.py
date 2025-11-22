from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.application.auth.ports.clock_port import ClockPort
from app.application.profile.ports.profile_repository_port import ProfileRepositoryPort
from app.application.target.dto.target_dto import CreateTargetInputDTO, TargetDTO
from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.application.target.ports.target_generator_port import TargetGeneratorPort
from app.domain.auth.errors import UserNotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.profile.entities import Profile
from app.domain.target import errors as target_errors
from app.domain.target.entities import TargetDefinition
from app.domain.target.value_objects import TargetId


class CreateTargetUseCase:
    """
    新しいターゲットを作成するユースケース。

    - プロフィール情報 + 目標情報 (GoalType / ActivityLevel / 説明) を元に、
      TargetGeneratorPort (LLM / ルールベース) を用いて 17栄養素のターゲット値を決定する。
    - ユーザーごとのターゲット数は最大 MAX_TARGETS_PER_USER 件まで。
    - まだアクティブなターゲットが無ければ、このターゲットを is_active=True にする。
    """

    MAX_TARGETS_PER_USER = 5

    def __init__(
        self,
        uow: TargetUnitOfWorkPort,
        profile_repo: ProfileRepositoryPort,
        generator: TargetGeneratorPort,
        clock: ClockPort,
    ) -> None:
        self._uow = uow
        self._profile_repo = profile_repo
        self._generator = generator
        self._clock = clock

    def execute(self, input_dto: CreateTargetInputDTO) -> TargetDTO:
        user_id_vo = UserId(input_dto.user_id)

        # プロフィールの存在確認
        profile: Profile | None = self._profile_repo.get_by_user_id(user_id_vo)
        if profile is None:
            # プロフィールが無い状態でターゲットは作らせない
            raise UserNotFoundError("Profile is required to create a target.")

        now = self._clock.now()

        with self._uow as uow:
            # 上限チェック
            current_count = uow.target_repo.count_for_user(user_id_vo)
            if current_count >= self.MAX_TARGETS_PER_USER:
                raise target_errors.MaxTargetsReachedError(
                    f"User {user_id_vo.value} cannot have more than {self.MAX_TARGETS_PER_USER} targets."
                )

            # 17栄養素のターゲット値を Generator から生成
            generated = self._generator.generate(
                profile=profile,
                goal_type=input_dto.goal_type,
                activity_level=input_dto.activity_level,
                goal_description=input_dto.goal_description,
            )

            # 既存のアクティブターゲットの有無
            has_active = uow.target_repo.get_active_for_user(
                user_id_vo) is not None

            target = TargetDefinition(
                id=TargetId(str(uuid4())),
                user_id=user_id_vo,
                title=input_dto.title,
                goal_type=input_dto.goal_type,
                goal_description=input_dto.goal_description,
                activity_level=input_dto.activity_level,
                nutrients=generated.nutrients,
                is_active=not has_active,  # まだアクティブが無ければ True
                created_at=now,
                updated_at=now,
                llm_rationale=generated.rationale,
                disclaimer=generated.disclaimer,
            )

            saved = uow.target_repo.save(target)
            # commit は UoW の __exit__ で行われる

        return TargetDTO.from_entity(saved)
