from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.engine import Result, Row
from typing import List, Any, Protocol
from datetime import date
from app.application.calendar.dto.calendar_dto import MonthlyCalendarDto
from app.application.calendar.ports.calendar_repository_port import CalendarRepositoryPort
from app.domain.calendar.entities import CalendarDaySnapshot


class CalendarQueryRow(Protocol):
    """カレンダークエリ結果の行を表す型プロトコル"""
    calendar_date: date
    has_meal_logs: bool
    nutrition_achievement: float | None
    has_daily_report: bool


class SqlAlchemyCalendarRepository(CalendarRepositoryPort):
    """SQLAlchemy を使ったカレンダーリポジトリ実装"""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_monthly_summary(
        self,
        request: MonthlyCalendarDto
    ) -> List[CalendarDaySnapshot]:
        """最適化されたSQL CTEクエリで月次データを取得"""

        # 月の開始日と終了日を計算
        start_date = f"{request.year}-{request.month:02d}-01"

        # 月末日を計算（次の月の1日から1日引く）
        if request.month == 12:
            end_year = request.year + 1
            end_month = 1
        else:
            end_year = request.year
            end_month = request.month + 1
        end_date = f"{end_year}-{end_month:02d}-01"

        # 最適化されたCTEクエリ
        query = text("""
            WITH date_series AS (
                SELECT generate_series(
                    :start_date::date,
                    (:end_date::date - interval '1 day')::date,
                    '1 day'::interval
                )::date AS calendar_date
            ),
            meal_summary AS (
                SELECT
                    fe.date,
                    COUNT(*) > 0 AS has_meals
                FROM food_entries fe
                WHERE fe.user_id = :user_id
                    AND fe.date >= :start_date::date
                    AND fe.date < :end_date::date
                    AND fe.deleted_at IS NULL
                GROUP BY fe.date
            ),
            nutrition_summary AS (
                SELECT
                    dns.date,
                    CASE
                        WHEN target.id IS NOT NULL THEN
                            ROUND(AVG(CASE
                                WHEN tn.amount > 0 THEN (dnn.value / tn.amount * 100)
                                ELSE 0
                            END))
                        ELSE NULL
                    END AS achievement_percentage
                FROM daily_nutrition_summaries dns
                JOIN daily_nutrition_nutrients dnn ON dns.id = dnn.daily_nutrition_summary_id
                LEFT JOIN targets target ON target.user_id = :user_id
                    AND target.is_active = true
                    AND target.deleted_at IS NULL
                LEFT JOIN target_nutrients tn ON target.id = tn.target_id
                    AND dnn.code = tn.code
                WHERE dns.user_id = :user_id
                    AND dns.date >= :start_date::date
                    AND dns.date < :end_date::date
                    AND dns.deleted_at IS NULL
                GROUP BY dns.date, target.id
            ),
            report_summary AS (
                SELECT
                    dnr.date,
                    COUNT(*) > 0 AS has_report
                FROM daily_nutrition_reports dnr
                WHERE dnr.user_id = :user_id
                    AND dnr.date >= :start_date::date
                    AND dnr.date < :end_date::date
                    AND dnr.deleted_at IS NULL
                GROUP BY dnr.date
            )
            SELECT
                ds.calendar_date,
                COALESCE(ms.has_meals, false) AS has_meal_logs,
                ns.achievement_percentage AS nutrition_achievement,
                COALESCE(rs.has_report, false) AS has_daily_report
            FROM date_series ds
            LEFT JOIN meal_summary ms ON ds.calendar_date = ms.date
            LEFT JOIN nutrition_summary ns ON ds.calendar_date = ns.date
            LEFT JOIN report_summary rs ON ds.calendar_date = rs.date
            ORDER BY ds.calendar_date;
        """)

        result: Result[Row[Any]] = self._session.execute(query, {
            'user_id': request.user_id,
            'start_date': start_date,
            'end_date': end_date
        })

        days: List[CalendarDaySnapshot] = []
        row: CalendarQueryRow
        for row in result:  # type: ignore[assignment]
            days.append(CalendarDaySnapshot(
                date=row.calendar_date.strftime('%Y-%m-%d'),
                has_meal_logs=row.has_meal_logs,
                nutrition_achievement=int(row.nutrition_achievement) if row.nutrition_achievement is not None else None,
                has_daily_report=row.has_daily_report
            ))

        return days
