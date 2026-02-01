import pytest
from app.application.calendar.use_cases.get_monthly_calendar import GetMonthlyCalendarUseCase
from app.application.calendar.dto.calendar_dto import MonthlyCalendarDto
from app.domain.calendar.errors import InvalidDateRangeError
from tests.fakes.calendar_repositories import InMemoryCalendarRepository
from tests.fakes.calendar_uow import FakeCalendarUnitOfWork


class TestGetMonthlyCalendarUseCase:
    """GetMonthlyCalendarUseCase のテスト"""

    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        self.calendar_repo = InMemoryCalendarRepository()
        self.uow = FakeCalendarUnitOfWork(self.calendar_repo)
        self.use_case = GetMonthlyCalendarUseCase(self.uow)

    def test_get_monthly_calendar_success(self):
        """正常な月次カレンダー取得のテスト"""
        user_id = "user123"

        # テストデータをセットアップ
        self.calendar_repo.add_meal_log(user_id, "2024-12-01", True)
        self.calendar_repo.add_nutrition_achievement(user_id, "2024-12-01", 85)
        self.calendar_repo.add_daily_report(user_id, "2024-12-01", True)

        self.calendar_repo.add_meal_log(user_id, "2024-12-02", False)
        # 12-02は栄養達成度なし（目標なし）
        self.calendar_repo.add_daily_report(user_id, "2024-12-02", False)

        self.calendar_repo.add_meal_log(user_id, "2024-12-03", True)
        self.calendar_repo.add_nutrition_achievement(user_id, "2024-12-03", 75)
        # 12-03はレポートなし

        # テスト実行
        request = MonthlyCalendarDto(
            user_id=user_id,
            year=2024,
            month=12
        )

        result = self.use_case.execute(request)

        # 結果の検証
        assert result.year == 2024
        assert result.month == 12
        assert len(result.days) == 31  # 12月は31日

        # 12月1日の確認
        day1 = result.days[0]
        assert day1.date == "2024-12-01"
        assert day1.has_meal_logs is True
        assert day1.nutrition_achievement == 85
        assert day1.has_daily_report is True

        # 12月2日の確認
        day2 = result.days[1]
        assert day2.date == "2024-12-02"
        assert day2.has_meal_logs is False
        assert day2.nutrition_achievement is None  # 目標なし
        assert day2.has_daily_report is False

        # 12月3日の確認
        day3 = result.days[2]
        assert day3.date == "2024-12-03"
        assert day3.has_meal_logs is True
        assert day3.nutrition_achievement == 75
        assert day3.has_daily_report is False

    def test_get_february_calendar_regular_year(self):
        """平年2月のカレンダー取得テスト"""
        user_id = "user123"

        request = MonthlyCalendarDto(
            user_id=user_id,
            year=2023,  # 平年
            month=2
        )

        result = self.use_case.execute(request)

        assert result.year == 2023
        assert result.month == 2
        assert len(result.days) == 28  # 平年の2月は28日

        # 最初の日と最後の日を確認
        assert result.days[0].date == "2023-02-01"
        assert result.days[27].date == "2023-02-28"

    def test_get_february_calendar_leap_year(self):
        """うるう年2月のカレンダー取得テスト"""
        user_id = "user123"

        request = MonthlyCalendarDto(
            user_id=user_id,
            year=2024,  # うるう年
            month=2
        )

        result = self.use_case.execute(request)

        assert result.year == 2024
        assert result.month == 2
        assert len(result.days) == 29  # うるう年の2月は29日

        # 最初の日と最後の日を確認
        assert result.days[0].date == "2024-02-01"
        assert result.days[28].date == "2024-02-29"

    def test_invalid_month_raises_error(self):
        """不正な月でエラーが発生することのテスト"""
        user_id = "user123"

        # 月が0の場合
        request = MonthlyCalendarDto(
            user_id=user_id,
            year=2024,
            month=0
        )

        with pytest.raises(InvalidDateRangeError) as exc_info:
            self.use_case.execute(request)

        assert "Invalid month: 0" in str(exc_info.value)

        # 月が13の場合
        request = MonthlyCalendarDto(
            user_id=user_id,
            year=2024,
            month=13
        )

        with pytest.raises(InvalidDateRangeError) as exc_info:
            self.use_case.execute(request)

        assert "Invalid month: 13" in str(exc_info.value)

    def test_invalid_year_raises_error(self):
        """不正な年でエラーが発生することのテスト"""
        user_id = "user123"

        # 年が1999の場合（範囲外）
        request = MonthlyCalendarDto(
            user_id=user_id,
            year=1999,
            month=12
        )

        with pytest.raises(InvalidDateRangeError) as exc_info:
            self.use_case.execute(request)

        assert "Invalid year: 1999" in str(exc_info.value)

        # 年が3001の場合（範囲外）
        request = MonthlyCalendarDto(
            user_id=user_id,
            year=3001,
            month=1
        )

        with pytest.raises(InvalidDateRangeError) as exc_info:
            self.use_case.execute(request)

        assert "Invalid year: 3001" in str(exc_info.value)

    def test_empty_data_returns_empty_snapshots(self):
        """データが空の場合のテスト"""
        user_id = "user123"

        request = MonthlyCalendarDto(
            user_id=user_id,
            year=2024,
            month=1
        )

        result = self.use_case.execute(request)

        assert result.year == 2024
        assert result.month == 1
        assert len(result.days) == 31  # 1月は31日

        # すべての日がデフォルト値（食事ログなし、達成度なし、レポートなし）
        for day in result.days:
            assert day.has_meal_logs is False
            assert day.nutrition_achievement is None
            assert day.has_daily_report is False

    def test_different_user_data_isolation(self):
        """異なるユーザーのデータが分離されていることのテスト"""
        user1_id = "user1"
        user2_id = "user2"

        # user1のデータを追加
        self.calendar_repo.add_meal_log(user1_id, "2024-12-01", True)
        self.calendar_repo.add_nutrition_achievement(user1_id, "2024-12-01", 90)

        # user2のリクエスト
        request = MonthlyCalendarDto(
            user_id=user2_id,
            year=2024,
            month=12
        )

        result = self.use_case.execute(request)

        # user2にはuser1のデータが見えないことを確認
        day1 = result.days[0]
        assert day1.date == "2024-12-01"
        assert day1.has_meal_logs is False  # user1のデータは見えない
        assert day1.nutrition_achievement is None  # user1のデータは見えない
        assert day1.has_daily_report is False