from __future__ import annotations

from datetime import datetime, timezone

# === Application (DTO / Ports / Errors) =====================================

from app.application.target.dto.target_dto import (
    UpdateTargetInputDTO,
    UpdateTargetNutrientDTO,
    TargetDTO,
    TargetNutrientDTO,
)
from app.application.target.errors import TargetNotFoundError
from app.application.target.ports.uow_port import TargetUnitOfWorkPort

# === Domain (Entities / ValueObjects / Errors) ==============================

from app.domain.auth.value_objects import UserId
from app.domain.target.entities import TargetDefinition, TargetNutrient
from app.domain.target.errors import InvalidTargetNutrientError
from app.domain.target.value_objects import (
    TargetId,
    GoalType,
    ActivityLevel,
    NutrientAmount,
    NutrientSource,
)


class UpdateTargetUseCase:
    """
    TargetDefinition の「部分更新」を行うユースケース。

    - None のフィールドは更新しない（PATCH 的な挙動）
    - nutrients で指定された栄養素の amount / unit を上書きし、
      変更された栄養素の source を "manual" にする。
    - トランザクション境界は `with self._uow` の範囲。
      commit / rollback は UoW 側に委譲する。
    """

    def __init__(self, uow: TargetUnitOfWorkPort) -> None:
        self._uow = uow

    def execute(self, input_dto: UpdateTargetInputDTO) -> TargetDTO:
        """
        指定された TargetDefinition を部分更新し、更新後の TargetDTO を返す。

        Raises:
            TargetNotFoundError:
                対象のターゲットが存在しない、または現在のユーザーのものではない場合。
            InvalidTargetNutrientError:
                nutrients に未知の栄養素コードが含まれている場合。
        """
        user_id = UserId(input_dto.user_id)
        target_id = TargetId(input_dto.target_id)

        # UoW のスコープ = 1 トランザクション
        with self._uow as uow:
            target = uow.target_repo.get_by_id(
                user_id=user_id,
                target_id=target_id,
            )
            if target is None:
                # 所有者チェック込みで「見えないターゲットは存在しない扱い」にする
                raise TargetNotFoundError(
                    "Target not found or does not belong to the current user."
                )

            # DTO で指定された項目のみ Entity に反映
            _apply_updates(target, input_dto)

            # 更新時刻を現在時刻（UTC）で更新
            target.update_timestamp(datetime.now(timezone.utc))

            # 永続化（commit は UoW の __exit__ で行われる）
            uow.target_repo.save(target)

            # 更新後の状態を DTO に変換して返す
            return _to_dto(target)


# === 内部ヘルパー ==========================================================


def _apply_updates(target: TargetDefinition, dto: UpdateTargetInputDTO) -> None:
    """
    DTO で指定された項目だけを TargetDefinition に反映する。

    - None のフィールドは「更新しない」という意味で解釈する。
    - nutrients が None の場合は、栄養素リストは変更しない。
    """

    # ---- 単純フィールド（タイトル / 目標 / 活動レベルなど） ----------------

    if dto.title is not None:
        target.title = dto.title

    if dto.goal_type is not None:
        target.goal_type = GoalType(dto.goal_type)

    if dto.goal_description is not None:
        target.goal_description = dto.goal_description

    if dto.activity_level is not None:
        target.activity_level = ActivityLevel(dto.activity_level)

    if dto.llm_rationale is not None:
        target.llm_rationale = dto.llm_rationale

    if dto.disclaimer is not None:
        target.disclaimer = dto.disclaimer

    # ---- 栄養素リスト（部分更新） -------------------------------------------

    # nutrients が None のときは、栄養素リスト自体は一切触らない
    if dto.nutrients is None:
        return

    # code.value ごとに既存栄養素を引けるように辞書化しておく
    nutrient_by_code: dict[str, TargetNutrient] = {
        n.code.value: n for n in target.nutrients
    }

    for patch in dto.nutrients:
        _apply_nutrient_patch(nutrient_by_code, patch)


def _apply_nutrient_patch(
    nutrient_by_code: dict[str, TargetNutrient],
    patch: UpdateTargetNutrientDTO,
) -> None:
    """
    単一の栄養素について、UpdateTargetNutrientDTO の内容を反映する。

    - amount / unit は PATCH 的に更新（None は現状維持）。
    - 更新された栄養素の source は "manual" に固定。
    """
    nutrient = nutrient_by_code.get(patch.code)

    if nutrient is None:
        # 指定された code に対応する栄養素が存在しない場合はドメインエラー
        raise InvalidTargetNutrientError(
            f"Unknown nutrient code: {patch.code}")

    current_amount = nutrient.amount

    # PATCH 的な挙動: None なら既存値を引き継ぐ
    new_value = current_amount.value if patch.amount is None else patch.amount
    new_unit = current_amount.unit if patch.unit is None else patch.unit

    # NutrientAmount は frozen な ValueObject 想定なので、新インスタンスで差し替える
    nutrient.amount = NutrientAmount(
        value=new_value,
        unit=new_unit,
    )

    # ユーザーが明示的に値をいじったので manual 扱いにする
    nutrient.source = NutrientSource("manual")


def _to_dto(target: TargetDefinition) -> TargetDTO:
    """
    Domain の TargetDefinition を Application 層の TargetDTO に変換する。
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
