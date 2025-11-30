from __future__ import annotations

from datetime import date as DateType

from fastapi import APIRouter, Depends, Query, status

from app.api.http.schemas.daily_report import (
    GenerateDailyReportRequest,
    DailyNutritionReportResponse,
)
from app.api.http.dependencies.auth import get_current_user_dto
from app.application.auth.dto.auth_user_dto import AuthUserDTO

from app.di.container import (
    get_generate_daily_nutrition_report_use_case,
    get_get_daily_nutrition_report_use_case,
)

from app.application.nutrition.use_cases.generate_daily_nutrition_report import (
    GenerateDailyNutritionReportUseCase,
)
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.errors import (
    DailyLogNotCompletedError,
    DailyNutritionReportAlreadyExistsError,
)
from app.domain.meal.errors import DailyLogProfileNotFoundError  # フェーズ1で定義した想定
from app.domain.nutrition.daily_report import DailyNutritionReport
from app.application.nutrition.use_cases.get_daily_nutrition_report import GetDailyNutritionReportUseCase

router = APIRouter(tags=["DailyReport"])


def _report_to_response(report: DailyNutritionReport) -> DailyNutritionReportResponse:
    """
    Domain の DailyNutritionReport -> API レスポンススキーマ変換。
    """
    return DailyNutritionReportResponse(
        date=report.date,
        summary=report.summary,
        good_points=report.good_points,
        improvement_points=report.improvement_points,
        tomorrow_focus=report.tomorrow_focus,
    )


@router.post(
    "/nutrition/daily/report",
    response_model=DailyNutritionReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_daily_nutrition_report(
    body: GenerateDailyReportRequest,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: GenerateDailyNutritionReportUseCase = Depends(
        get_generate_daily_nutrition_report_use_case
    ),
):
    """
    指定した日の DailyNutritionReport を生成する。

    - 前提:
        - その日の食事ログが「記録完了」していること。
    - 失敗ケース:
        - DailyLogNotCompletedError
        - DailyNutritionReportAlreadyExistsError
        - Profile 未設定 など
    """

    user_id = UserId(current_user.id)
    target_date: DateType = body.date

    try:
        report = use_case.execute(user_id=user_id, date_=target_date)
    except DailyLogProfileNotFoundError as e:
        # プロフィール未設定 → 400 などにマッピングする想定
        # 実際には共通エラーハンドラ側で処理してもOK
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile is required before generating a daily report.",
        ) from e
    except DailyLogNotCompletedError as e:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Daily log is not completed for the specified date.",
        ) from e
    except DailyNutritionReportAlreadyExistsError as e:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Daily nutrition report already exists for the specified date.",
        ) from e

    return _report_to_response(report)


@router.get(
    "/nutrition/daily/report",
    response_model=DailyNutritionReportResponse,
)
def get_daily_nutrition_report(
    date: DateType = Query(..., description="レポート対象日 (YYYY-MM-DD)"),
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: GetDailyNutritionReportUseCase = Depends(
        get_get_daily_nutrition_report_use_case
    ),
):
    """
    指定した日の DailyNutritionReport を取得する。

    - 既に生成済みのレポートを読むだけ。
    - 存在しない場合は 404 を返す。
    """

    user_id = UserId(current_user.id)

    report = use_case.execute(
        user_id=user_id,
        date_=date,
    )
    if report is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily nutrition report not found for the specified date.",
        )

    return _report_to_response(report)
