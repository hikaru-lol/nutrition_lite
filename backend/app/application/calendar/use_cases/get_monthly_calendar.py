from app.application.calendar.dto.calendar_dto import MonthlyCalendarDto, MonthlyCalendarResultDto
from app.application.calendar.ports.calendar_unit_of_work_port import CalendarUnitOfWorkPort
from app.domain.calendar.errors import InvalidDateRangeError


class GetMonthlyCalendarUseCase:
    """月次カレンダー取得ユースケース"""

    def __init__(self, uow: CalendarUnitOfWorkPort):
        self._uow = uow

    def execute(self, request: MonthlyCalendarDto) -> MonthlyCalendarResultDto:
        """月次カレンダーを取得"""
        # バリデーション
        if not (1 <= request.month <= 12):
            raise InvalidDateRangeError(f"Invalid month: {request.month}")
        if not (2000 <= request.year <= 3000):
            raise InvalidDateRangeError(f"Invalid year: {request.year}")

        # UoW を使ってリポジトリにアクセス
        with self._uow:
            days = self._uow.calendar_repo.get_monthly_summary(request)

            return MonthlyCalendarResultDto(
                year=request.year,
                month=request.month,
                days=days
            )
