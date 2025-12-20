from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

# === API (schemas / dependencies) ==========================================
from app.api.http.dependencies.auth import get_current_user_dto
from app.api.http.schemas.errors import ErrorResponse
from app.api.http.schemas.profile import ProfileRequest, ProfileResponse

# === Application (DTO / UseCase) ============================================
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.profile.dto.profile_dto import UpsertProfileInputDTO
from app.application.profile.use_cases.get_my_profile import GetMyProfileUseCase
from app.application.profile.use_cases.upsert_profile import UpsertProfileUseCase

# === DI =====================================================================
from app.di.container import (
    get_my_profile_use_case,
    get_upsert_profile_use_case,
)

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get(
    "/me",
    response_model=ProfileResponse,
    responses={
        401: {"model": ErrorResponse},
    },
)
def get_my_profile(
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: GetMyProfileUseCase = Depends(get_my_profile_use_case),
) -> ProfileResponse:
    """
    現在ログイン中ユーザーのプロフィールを取得する。
    プロフィールが存在しない場合は UserNotFoundError などが発生し、
    auth_error_handler 経由で 401 や適切なエラーとして返される想定。
    """
    dto = use_case.execute(current_user.id)
    # DTO と ProfileResponse のフィールド名が一致しているので、そのまま詰め替え可能
    return ProfileResponse.model_validate(dto.__dict__)


@router.put(
    "/me",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
    },
)
def upsert_my_profile(
    request: ProfileRequest,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: UpsertProfileUseCase = Depends(get_upsert_profile_use_case),
) -> ProfileResponse:
    """
    現在ログイン中ユーザーのプロフィールを作成 / 更新する。

    現時点では画像は受け取らず、テキスト情報のみ更新。
    画像は後で別エンドポイントや multipart PATCH などで拡張する前提。
    """
    input_dto = UpsertProfileInputDTO(
        user_id=current_user.id,
        sex=request.sex,
        birthdate=request.birthdate,
        height_cm=request.height_cm,
        weight_kg=request.weight_kg,
        image_content=None,
        image_content_type=None,
        meals_per_day=request.meals_per_day,
    )

    dto = use_case.execute(input_dto)
    return ProfileResponse.model_validate(dto.__dict__)
