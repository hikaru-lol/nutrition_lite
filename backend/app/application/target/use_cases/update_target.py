from __future__ import annotations

from app.application.auth.ports.clock_port import ClockPort
from app.application.target.dto.target_dto import TargetDTO, UpdateTargetInputDTO, TargetNutrientDTO
from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.target import errors as target_errors
from app.domain.target.entities import TargetNutrient
from app.domain.target.value_objects import TargetId, NutrientAmount, NutrientSource


class UpdateTargetUseCase:
    """
    既存ターゲットを手動で編集するユースケース。

    - LLM は利用しない。
    - 栄養素を編集する場合、NutrientSource は "manual" に更新される。
    """

    def __init__(self, uow: TargetUnitOfWorkPort, clock: ClockPort) -> None:
        self._uow = uow
        self._clock = clock

    def execute(self, input_dto: UpdateTargetInputDTO) -> TargetDTO:
        user_id_vo = UserId(input_dto.user_id)
        target_id_vo = TargetId(input_dto.target_id)
        now = self._clock.now()

        with self._uow as uow:
            target = uow.target_repo.get_by_id(user_id_vo, target_id_vo)
            if target is None:
                raise target_errors.TargetNotFoundError("Target not found.")

            # メタ情報の更新
            if input_dto.title is not None:
                target.title = input_dto.title
            if input_dto.goal_type is not None:
                target.goal_type = input_dto.goal_type
            if input_dto.goal_description is not None:
                target.goal_description = input_dto.goal_description
            if input_dto.activity_level is not None:
                target.activity_level = input_dto.activity_level

            # 栄養素の更新（全置き換え or 部分更新は要件に応じて調整）
            if input_dto.nutrients is not None:
                new_nutrients: list[TargetNutrient] = []
                for n in input_dto.nutrients:
                    if not isinstance(n, TargetNutrientDTO):
                        # 型の整合性を保つための簡易チェック（テスト時のミス防止）
                        raise ValueError(
                            "Expected TargetNutrientDTO in nutrients.")
                    new_nutrients.append(
                        TargetNutrient(
                            code=n.code,
                            amount=NutrientAmount(value=n.amount, unit=n.unit),
                            # 手動編集なので source は "manual" に固定
                            source=NutrientSource("manual"),
                        )
                    )
                target.nutrients = new_nutrients

            target.update_timestamp(now)

            saved = uow.target_repo.save(target)

        return TargetDTO.from_entity(saved)
