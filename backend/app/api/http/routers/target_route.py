from __future__ import annotations

from fastapi import APIRouter, Depends, Path, status

from app.api.http.schemas.auth import ErrorResponse
from app.api.http.schemas.target import (
    TargetCreateRequest,
    TargetUpdateRequest,
    TargetResponse,
    TargetsResponse,
    Target,
    TargetNutrient,
)
from app.api.http.dependencies.auth import get_current_user_dto
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.target.dto.target_dto import (
    TargetDTO,
    TargetNutrientDTO,
    CreateTargetInputDTO,
    UpdateTargetInputDTO,
    UpdateTargetNutrientDTO,
    ActivateTargetInputDTO,
)
from app.application.target.use_cases.create_target import CreateTargetUseCase
from app.application.target.use_cases.list_targets import ListTargetsUseCase
from app.application.target.use_cases.get_active_target import GetActiveTargetUseCase
from app.application.target.use_cases.get_target import GetTargetUseCase
from app.application.target.use_cases.update_target import UpdateTargetUseCase
from app.application.target.use_cases.activate_target import ActivateTargetUseCase
from app.di.container import (
    get_create_target_use_case,
    get_list_targets_use_case,
    get_get_active_target_use_case,
    get_get_target_use_case,
    get_update_target_use_case,
    get_activate_target_use_case,
)

router = APIRouter(prefix="/targets", tags=["Target"])


def _to_target_schema(dto: TargetDTO) -> Target:
    """
    application層の TargetDTO から API用 Target スキーマへ変換するヘルパ。
    """
    return Target(
        id=dto.id,
        user_id=dto.user_id,
        title=dto.title,
        goal_type=dto.goal_type,
        goal_description=dto.goal_description,
        activity_level=dto.activity_level,
        is_active=dto.is_active,
        nutrients=[
            TargetNutrient(
                code=n.code,
                amount=n.amount,
                unit=n.unit,
                source=n.source,
            )
            for n in dto.nutrients
        ],
        llm_rationale=dto.llm_rationale,
        disclaimer=dto.disclaimer,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


@router.get(
    "",
    response_model=TargetsResponse,
    responses={401: {"model": ErrorResponse}},
)
def list_targets(
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: ListTargetsUseCase = Depends(get_list_targets_use_case),
) -> TargetsResponse:
    """
    現在ログイン中のユーザーのターゲット一覧を取得する。
    """
    dtos = use_case.execute(current_user.id)
    items = [_to_target_schema(dto) for dto in dtos]
    return TargetsResponse(items=items)


@router.post(
    "",
    response_model=TargetResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},  # プロフィールがない場合など
        409: {"model": ErrorResponse},  # MAX_TARGETS_REACHED など
    },
)
def create_target(
    body: TargetCreateRequest,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: CreateTargetUseCase = Depends(get_create_target_use_case),
) -> TargetResponse:
    """
    新しいターゲットを作成する。

    - Profile 情報は UseCase 内で ProfileRepositoryPort を通じて取得。
    """
    input_dto = CreateTargetInputDTO(
        user_id=current_user.id,
        sex=None,           # プロフィールから取る設計なら DTO から外してOK
        birthdate=None,
        height_cm=None,
        weight_kg=None,
        goal_type=body.goal_type,
        activity_level=body.activity_level,
        goal_description=body.goal_description,
        title=body.title,
    )
    dto: TargetDTO = use_case.execute(input_dto)
    return TargetResponse(target=_to_target_schema(dto))


@router.get(
    "/active",
    response_model=TargetResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def get_active_target(
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: GetActiveTargetUseCase = Depends(get_get_active_target_use_case),
) -> TargetResponse:
    """
    現在のアクティブなターゲットを取得する。
    """
    dto: TargetDTO = use_case.execute(current_user.id)
    return TargetResponse(target=_to_target_schema(dto))


@router.get(
    "/{target_id}",
    response_model=TargetResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def get_target(
    target_id: str = Path(..., description="Target ID (UUID)"),
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: GetTargetUseCase = Depends(get_get_target_use_case),
) -> TargetResponse:
    """
    指定されたターゲットを取得する。
    """
    dto: TargetDTO = use_case.execute(
        user_id=current_user.id, target_id=target_id)
    return TargetResponse(target=_to_target_schema(dto))


@router.put(
    "/{target_id}",
    response_model=TargetResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def update_target(
    target_id: str = Path(..., description="Target ID (UUID)"),
    body: TargetUpdateRequest = ...,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: UpdateTargetUseCase = Depends(get_update_target_use_case),
) -> TargetResponse:
    """
    既存のターゲットを更新する。

    - 減量／増量の目標や活動量の変更
    - 特定の栄養素の amount/unit の手動調整 など
    """

    nutrient_updates: list[NutrientUpdateDTO] | None = None
    if body.nutrients:
        nutrient_updates = [
            NutrientUpdateDTO(
                code=n.code,
                amount=n.amount,
                unit=n.unit,
            )
            for n in body.nutrients
        ]

    input_dto = UpdateTargetInputDTO(
        user_id=current_user.id,
        target_id=target_id,
        title=body.title,
        goal_type=body.goal_type,
        goal_description=body.goal_description,
        activity_level=body.activity_level,
        nutrients=nutrient_updates,
    )

    dto: TargetDTO = use_case.execute(input_dto)
    return TargetResponse(target=_to_target_schema(dto))


@router.post(
    "/{target_id}/activate",
    response_model=TargetResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def activate_target(
    target_id: str = Path(..., description="Target ID (UUID)"),
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: ActivateTargetUseCase = Depends(get_activate_target_use_case),
) -> TargetResponse:
    """
    指定したターゲットをアクティブなターゲットとしてマークする。
    以前アクティブだったターゲットは非アクティブになる。
    """
    input_dto = ActivateTargetInputDTO(
        user_id=current_user.id,
        target_id=target_id,
    )
    dto: TargetDTO = use_case.execute(input_dto)
    return TargetResponse(target=_to_target_schema(dto))
