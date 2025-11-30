from __future__ import annotations

from datetime import date as DateType

# === Third-party ============================================================
from fastapi import APIRouter, Depends, Query, status

# === API (schemas / dependencies) ==========================================
from app.api.http.dependencies.auth import get_current_user_dto
from app.api.http.schemas.daily_report import (
    DailyNutritionReportResponse,
    GenerateDailyReportRequest,
)

# === Application (DTO / UseCase) ============================================
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.nutrition.use_cases.generate_daily_nutrition_report import (
    GenerateDailyNutritionReportUseCase,
)
from app.application.nutrition.use_cases.get_daily_nutrition_report import (
    GetDailyNutritionReportUseCase,
)

# === Domain ================================================================
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_report import DailyNutritionReport

# === DI =====================================================================
from app.di.container import (
    get_generate_daily_nutrition_report_use_case,
    get_get_daily_nutrition_report_use_case,
)

router = APIRouter(tags=["DailyReport"])


# === Helpers ===============================================================


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


# === Routes ================================================================


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
) -> DailyNutritionReportResponse:
    """
    指定した日の DailyNutritionReport を生成する。

    - 前提:
        - その日の食事ログが「記録完了」していること。
    - 失敗ケース（例）:
        - DailyLogNotCompletedError
        - DailyNutritionReportAlreadyExistsError
        - DailyLogProfileNotFoundError など
      → ここでは捕まえず、共通エラーハンドラで HTTP にマッピングする。
    """

    user_id = UserId(current_user.id)
    target_date: DateType = body.date

    report = use_case.execute(user_id=user_id, date_=target_date)
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
) -> DailyNutritionReportResponse:
    """
    指定した日の DailyNutritionReport を取得する。

    - 既に生成済みのレポートを読むだけ。
    - 存在しない場合は 404 を返す。
    """

    from fastapi import HTTPException

    user_id = UserId(current_user.id)

    report = use_case.execute(
        user_id=user_id,
        date_=date,
    )
    if report is None:
        # ここだけはまだ HTTPException 直書きのまま。
        # 必要なら専用エラーを定義して共通ハンドラに寄せても OK。
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily nutrition report not found for the specified date.",
        )

    return _report_to_response(report)
