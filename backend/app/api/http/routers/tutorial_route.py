"""チュートリアル機能のAPIルーター"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.http.dependencies.auth import get_current_user_dto
from app.api.http.schemas.tutorial import TutorialCompleteResponse, TutorialStatusResponse
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.tutorial.dto.tutorial_dto import (
    CompleteTutorialInputDTO,
    GetTutorialStatusInputDTO,
)
from app.application.tutorial.use_cases.complete_tutorial import CompleteTutorialUseCase
from app.application.tutorial.use_cases.get_tutorial_status import GetTutorialStatusUseCase
from app.domain.tutorial.errors import InvalidTutorialIdError, TutorialAlreadyCompletedError
from app.di.container import get_get_tutorial_status_use_case, get_complete_tutorial_use_case

router = APIRouter(prefix="/tutorials", tags=["tutorial"])


@router.get("/status", response_model=TutorialStatusResponse)
def get_tutorial_status(
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: GetTutorialStatusUseCase = Depends(get_get_tutorial_status_use_case),
) -> TutorialStatusResponse:
    """ユーザーのチュートリアル完了状況を取得

    Returns:
        TutorialStatusResponse: 完了済みチュートリアルIDのリスト
    """
    input_dto = GetTutorialStatusInputDTO(user_id=current_user.id)
    result = use_case.execute(input_dto)

    return TutorialStatusResponse(completed=result.completed_tutorial_ids)


@router.post(
    "/{tutorial_id}/complete",
    status_code=status.HTTP_200_OK,
    response_model=TutorialCompleteResponse,
)
def complete_tutorial(
    tutorial_id: str,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: CompleteTutorialUseCase = Depends(get_complete_tutorial_use_case),
) -> TutorialCompleteResponse:
    """チュートリアルを完了としてマーク

    Args:
        tutorial_id: 完了するチュートリアルのID

    Returns:
        TutorialCompleteResponse: 完了結果

    Raises:
        HTTPException: 無効なチュートリアルIDまたは既に完了済みの場合
    """
    try:
        input_dto = CompleteTutorialInputDTO(
            user_id=current_user.id,
            tutorial_id=tutorial_id,
        )
        result = use_case.execute(input_dto)

        return TutorialCompleteResponse(
            tutorial_id=result.tutorial_id,
            completed_at=result.completed_at.isoformat(),
        )

    except InvalidTutorialIdError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tutorial ID: {e.tutorial_id}",
        ) from e

    except TutorialAlreadyCompletedError as e:
        # 既に完了済みの場合は冪等性を保つため成功レスポンスを返す
        # フロントエンドにとっては「完了状態になった」という結果は同じ
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail=f"Tutorial already completed",
        ) from e