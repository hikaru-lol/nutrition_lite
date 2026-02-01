import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session
from app.infra.db.repositories.calendar_repository import SqlAlchemyCalendarRepository
from app.application.calendar.dto.calendar_dto import MonthlyCalendarDto
from app.domain.calendar.entities import CalendarDaySnapshot


class TestSqlAlchemyCalendarRepository:
    """SqlAlchemyCalendarRepository のテスト"""

    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        self.session_mock = Mock(spec=Session)
        self.repository = SqlAlchemyCalendarRepository(self.session_mock)

    def test_get_monthly_summary_with_data(self):
        """データがある場合の月次サマリー取得テスト"""
        # モックデータの準備
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([
            # 12月1日のデータ
            MagicMock(
                calendar_date=MockDate(2024, 12, 1),
                has_meal_logs=True,
                nutrition_achievement=85,
                has_daily_report=True
            ),
            # 12月2日のデータ
            MagicMock(
                calendar_date=MockDate(2024, 12, 2),
                has_meal_logs=False,
                nutrition_achievement=None,
                has_daily_report=False
            ),
            # 12月3日のデータ
            MagicMock(
                calendar_date=MockDate(2024, 12, 3),
                has_meal_logs=True,
                nutrition_achievement=75,
                has_daily_report=False
            ),
        ]))

        self.session_mock.execute.return_value = mock_result

        # テスト実行
        request = MonthlyCalendarDto(
            user_id="user123",
            year=2024,
            month=12
        )

        result = self.repository.get_monthly_summary(request)

        # セッションのexecuteが呼ばれたことを確認
        self.session_mock.execute.assert_called_once()

        # 呼び出されたクエリパラメータを確認
        call_args = self.session_mock.execute.call_args
        params = call_args.args[1] if len(call_args.args) > 1 else call_args.kwargs
        assert params['user_id'] == 'user123'
        assert params['start_date'] == '2024-12-01'
        assert params['end_date'] == '2025-01-01'

        # 結果を確認
        assert len(result) == 3

        # 1日目の確認
        day1 = result[0]
        assert isinstance(day1, CalendarDaySnapshot)
        assert day1.date == "2024-12-01"
        assert day1.has_meal_logs is True
        assert day1.nutrition_achievement == 85
        assert day1.has_daily_report is True

        # 2日目の確認
        day2 = result[1]
        assert day2.date == "2024-12-02"
        assert day2.has_meal_logs is False
        assert day2.nutrition_achievement is None
        assert day2.has_daily_report is False

        # 3日目の確認
        day3 = result[2]
        assert day3.date == "2024-12-03"
        assert day3.has_meal_logs is True
        assert day3.nutrition_achievement == 75
        assert day3.has_daily_report is False

    def test_get_monthly_summary_february_regular_year(self):
        """平年2月の月次サマリー取得テスト（日付計算確認）"""
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([]))
        self.session_mock.execute.return_value = mock_result

        # テスト実行
        request = MonthlyCalendarDto(
            user_id="user123",
            year=2023,  # 平年
            month=2
        )

        self.repository.get_monthly_summary(request)

        # 呼び出されたクエリパラメータを確認
        call_args = self.session_mock.execute.call_args
        params = call_args.args[1] if len(call_args.args) > 1 else call_args.kwargs
        assert params['start_date'] == '2023-02-01'
        assert params['end_date'] == '2023-03-01'

    def test_get_monthly_summary_december(self):
        """12月の月次サマリー取得テスト（年跨ぎの日付計算確認）"""
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([]))
        self.session_mock.execute.return_value = mock_result

        # テスト実行
        request = MonthlyCalendarDto(
            user_id="user123",
            year=2024,
            month=12
        )

        self.repository.get_monthly_summary(request)

        # 呼び出されたクエリパラメータを確認
        call_args = self.session_mock.execute.call_args
        params = call_args.args[1] if len(call_args.args) > 1 else call_args.kwargs
        assert params['start_date'] == '2024-12-01'
        assert params['end_date'] == '2025-01-01'  # 年が変わる

    def test_get_monthly_summary_nutrition_achievement_conversion(self):
        """栄養達成度のint変換テスト"""
        # float値が返される場合のテスト
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([
            MagicMock(
                calendar_date=MockDate(2024, 12, 1),
                has_meal_logs=True,
                nutrition_achievement=85.7,  # floatで返される
                has_daily_report=True
            ),
        ]))

        self.session_mock.execute.return_value = mock_result

        request = MonthlyCalendarDto(
            user_id="user123",
            year=2024,
            month=12
        )

        result = self.repository.get_monthly_summary(request)

        # float が int に変換されることを確認
        assert result[0].nutrition_achievement == 85

    def test_get_monthly_summary_empty_result(self):
        """空の結果の場合のテスト"""
        mock_result = MagicMock()
        mock_result.__iter__ = Mock(return_value=iter([]))
        self.session_mock.execute.return_value = mock_result

        request = MonthlyCalendarDto(
            user_id="user123",
            year=2024,
            month=1
        )

        result = self.repository.get_monthly_summary(request)

        assert result == []

    def test_session_passed_correctly(self):
        """セッションが正しく保持されることのテスト"""
        assert self.repository._session is self.session_mock


class MockDate:
    """日付オブジェクトのモック"""

    def __init__(self, year: int, month: int, day: int):
        self.year = year
        self.month = month
        self.day = day

    def strftime(self, format_str: str) -> str:
        if format_str == '%Y-%m-%d':
            return f"{self.year}-{self.month:02d}-{self.day:02d}"
        return ""