from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, status

# === API (schemas / dependencies) ==========================================
from app.api.http.dependencies.auth import get_current_user_dto
from app.api.http.schemas.auth import ErrorResponse
from app.api.http.schemas.target import (
    CreateTargetRequest,
    TargetListResponse,
    TargetResponse,
    UpdateTargetRequest,
    target_dto_to_schema,
    target_list_dto_to_schema,
)

# === Application (DTO / UseCase) ============================================
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.target.dto.target_dto import (
    ActivateTargetInputDTO,
    CreateTargetInputDTO,
    GetActiveTargetInputDTO,
    GetTargetInputDTO,
    ListTargetsInputDTO,
    UpdateTargetInputDTO,
    UpdateTargetNutrientDTO,
)
from app.application.target.use_cases.activate_target import ActivateTargetUseCase
from app.application.target.use_cases.create_target import CreateTargetUseCase
from app.application.target.use_cases.get_active_target import GetActiveTargetUseCase
from app.application.target.use_cases.get_target import GetTargetUseCase
from app.application.target.use_cases.list_targets import ListTargetsUseCase
from app.application.target.use_cases.update_target import UpdateTargetUseCase

# === DI =====================================================================
from app.di.container import (
    get_activate_target_use_case,
    get_create_target_use_case,
    get_get_active_target_use_case,
    get_get_target_use_case,
    get_list_targets_use_case,
    get_update_target_use_case,
)

router = APIRouter(prefix="/targets", tags=["Target"])

logger = logging.getLogger("target_route")


# === Routes ================================================================


# --- POST /targets  ターゲット作成 ----------------------------------------
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=TargetResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},  # 上限超えなどドメインエラーを想定
    },
)
def create_target(
    request: CreateTargetRequest,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: CreateTargetUseCase = Depends(get_create_target_use_case),
) -> TargetResponse:
    """
    新しいターゲットを作成する。
    17栄養素はサーバ側で TargetGenerator により決定される。
    """
    input_dto = CreateTargetInputDTO(
        user_id=str(current_user.id),
        title=request.title,
        goal_type=request.goal_type,           # Literal[str] -> str
        goal_description=request.goal_description,
        activity_level=request.activity_level,
    )

    result = use_case.execute(input_dto)

    logger.info(
        "Target created: user_id=%s target_id=%s",
        current_user.id,
        result.id,
    )

    return target_dto_to_schema(result)


# --- GET /targets  ターゲット一覧 -----------------------------------------
@router.get(
    "",
    response_model=TargetListResponse,
    responses={
        401: {"model": ErrorResponse},
    },
)
def list_targets(
    limit: int | None = None,
    offset: int = 0,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: ListTargetsUseCase = Depends(get_list_targets_use_case),
) -> TargetListResponse:
    """
    現在のユーザーのターゲット一覧を取得する。
    """
    input_dto = ListTargetsInputDTO(
        user_id=str(current_user.id),
        limit=limit,
        offset=offset,
    )

    result = use_case.execute(input_dto)
    return target_list_dto_to_schema(result)


# --- GET /targets/active  アクティブターゲット取得 -----------------------
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
    現在アクティブなターゲットを取得する。
    """
    input_dto = GetActiveTargetInputDTO(user_id=str(current_user.id))
    result = use_case.execute(input_dto)
    return target_dto_to_schema(result)


# --- GET /targets/{target_id}  ターゲット1件取得 -------------------------
@router.get(
    "/{target_id}",
    response_model=TargetResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def get_target(
    target_id: str,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: GetTargetUseCase = Depends(get_get_target_use_case),
) -> TargetResponse:
    """
    指定 ID のターゲットを1件取得する。
    """
    input_dto = GetTargetInputDTO(
        user_id=str(current_user.id),
        target_id=target_id,
    )

    result = use_case.execute(input_dto)
    return target_dto_to_schema(result)


# --- PATCH /targets/{target_id}  ターゲット部分更新 ----------------------
@router.patch(
    "/{target_id}",
    response_model=TargetResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def update_target(
    target_id: str,
    request: UpdateTargetRequest,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: UpdateTargetUseCase = Depends(get_update_target_use_case),
) -> TargetResponse:
    """
    ターゲットの部分更新（PATCH）。
    """
    nutrients_dto: list[UpdateTargetNutrientDTO] | None = None
    if request.nutrients is not None:
        nutrients_dto = [
            UpdateTargetNutrientDTO(
                code=n.code,
                amount=n.amount,
                unit=n.unit,
            )
            for n in request.nutrients
        ]

    input_dto = UpdateTargetInputDTO(
        user_id=str(current_user.id),
        target_id=target_id,
        title=request.title,
        goal_type=request.goal_type,
        goal_description=request.goal_description,
        activity_level=request.activity_level,
        llm_rationale=request.llm_rationale,
        disclaimer=request.disclaimer,
        nutrients=nutrients_dto,
    )

    result = use_case.execute(input_dto)

    logger.info(
        "Target updated: user_id=%s target_id=%s",
        current_user.id,
        target_id,
    )

    return target_dto_to_schema(result)


# --- POST /targets/{target_id}/activate  ターゲットをアクティブ化 --------
@router.post(
    "/{target_id}/activate",
    response_model=TargetResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def activate_target(
    target_id: str,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: ActivateTargetUseCase = Depends(get_activate_target_use_case),
) -> TargetResponse:
    """
    指定したターゲットをアクティブ化する。
    （同一ユーザーの他のターゲットは非アクティブになる）
    """
    input_dto = ActivateTargetInputDTO(
        user_id=str(current_user.id),
        target_id=target_id,
    )

    result = use_case.execute(input_dto)

    logger.info(
        "Target activated: user_id=%s target_id=%s",
        current_user.id,
        target_id,
    )

    return target_dto_to_schema(result)
