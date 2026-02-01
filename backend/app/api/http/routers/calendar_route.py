from fastapi import APIRouter, Depends, HTTPException
from app.api.http.schemas.calendar import (
    MonthlyCalendarQuerySchema,
    MonthlyCalendarResponseSchema,
    CalendarDaySnapshotSchema
)
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.calendar.use_cases.get_monthly_calendar import GetMonthlyCalendarUseCase
from app.application.calendar.dto.calendar_dto import MonthlyCalendarDto, MonthlyCalendarResultDto
from app.api.http.dependencies.auth import get_current_user_dto
from app.domain.calendar.errors import CalendarError
from app.di.container import get_get_monthly_calendar_use_case

router = APIRouter()


@router.get(
    "/monthly-summary",
    response_model=MonthlyCalendarResponseSchema,
    summary="月次カレンダーサマリー取得",
    description="指定した年月の各日の食事ログ・達成度・レポート状況を取得"
)
def get_monthly_summary(
    query: MonthlyCalendarQuerySchema = Depends(),
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: GetMonthlyCalendarUseCase = Depends(
        get_get_monthly_calendar_use_case)
) -> MonthlyCalendarResponseSchema:
    """月次カレンダーサマリーを取得"""

    try:
        request_dto = MonthlyCalendarDto(
            user_id=current_user.id,
            year=query.year,
            month=query.month
        )

        result: MonthlyCalendarResultDto = use_case.execute(
            request_dto)

        return MonthlyCalendarResponseSchema(
            year=result.year,
            month=result.month,
            days=[
                CalendarDaySnapshotSchema(
                    date=day.date,
                    has_meal_logs=day.has_meal_logs,
                    nutrition_achievement=day.nutrition_achievement,
                    has_daily_report=day.has_daily_report
                )
                for day in result.days
            ]
        )

    except CalendarError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
