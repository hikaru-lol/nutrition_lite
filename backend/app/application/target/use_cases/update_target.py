from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from app.application.target.dto.target_dto import (
    UpdateTargetInputDTO,
    UpdateTargetNutrientDTO,
    TargetDTO,
    TargetNutrientDTO,
)
from app.domain.target.errors import TargetNotFoundError
from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.target.value_objects import (
    TargetId,
    GoalType,
    ActivityLevel,
    NutrientAmount,
    NutrientSource,
)

if TYPE_CHECKING:
    from app.domain.target.entities import TargetDefinition, TargetNutrient


class UpdateTargetUseCase:
    """
    TargetDefinition の「部分更新」を行うユースケース。

    - None のフィールドは更新しない（PATCH 的な挙動）
    - 栄養素が更新された場合、その nutrient.source は "manual" に切り替える想定
    """

    def __init__(self, uow: TargetUnitOfWorkPort) -> None:
        self._uow = uow

    def __call__(self, input_dto: UpdateTargetInputDTO) -> TargetDTO:
        user_id = UserId(input_dto.user_id)
        target_id = TargetId(input_dto.target_id)

        with self._uow as uow:
            target = uow.target_repo.get_by_id(
                user_id=user_id,
                target_id=target_id,
            )

            if target is None:
                raise TargetNotFoundError(
                    "Target not found or does not belong to the current user."
                )

            _apply_updates(target, input_dto)

            # updated_at を現在時刻に更新
            target.update_timestamp(datetime.now(timezone.utc))

            # SQLAlchemy の場合、save は no-op でもOK（Session がトラッキングしているため）
            uow.target_repo.save(target)

            return _to_dto(target)


# --- 内部ヘルパー -----------------------------------------------------


def _apply_updates(target: "TargetDefinition", dto: UpdateTargetInputDTO) -> None:
    """DTO で指定された項目だけを TargetDefinition に反映する。"""

    # ---- 単純フィールド ----
    if dto.title is not None:
        target.title = dto.title

    if dto.goal_type is not None:
        # GoalType は str Enum ("weight_loss" 等)
        target.goal_type = GoalType(dto.goal_type)

    if dto.goal_description is not None:
        target.goal_description = dto.goal_description

    if dto.activity_level is not None:
        target.activity_level = ActivityLevel(dto.activity_level)

    if dto.llm_rationale is not None:
        target.llm_rationale = dto.llm_rationale

    if dto.disclaimer is not None:
        target.disclaimer = dto.disclaimer

    # ---- 栄養素リスト ----
    if dto.nutrients is None:
        return

    # code.value で辞書化
    nutrient_by_code: dict[str, "TargetNutrient"] = {
        n.code.value: n for n in target.nutrients
    }

    for patch in dto.nutrients:
        _apply_nutrient_patch(nutrient_by_code, patch)


def _apply_nutrient_patch(
    nutrient_by_code: dict[str, "TargetNutrient"],
    patch: UpdateTargetNutrientDTO,
) -> None:
    # DTO は code を string で受け取るので、そのままキーにする
    nutrient = nutrient_by_code.get(patch.code)

    if nutrient is None:
        # 設計次第：
        # - 無視する
        # - ログだけ吐く
        # - 専用のエラーにする
        # といったバリエーションがある。ここではとりあえずエラー。
        raise ValueError(f"Unknown nutrient code: {patch.code}")

    current_amount = nutrient.amount

    new_value = current_amount.value if patch.amount is None else patch.amount
    new_unit = current_amount.unit if patch.unit is None else patch.unit

    # NutrientAmount は frozen dataclass なので、新インスタンスを作って差し替える
    nutrient.amount = NutrientAmount(
        value=new_value,
        unit=new_unit,
    )

    # ユーザーが明示的に値をいじったので manual 扱いにする
    nutrient.source = NutrientSource("manual")


def _to_dto(target: "TargetDefinition") -> TargetDTO:
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
