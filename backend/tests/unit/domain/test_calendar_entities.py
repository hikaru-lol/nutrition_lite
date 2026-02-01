import pytest
from app.domain.calendar.entities import CalendarDaySnapshot


class TestCalendarDaySnapshot:
    """CalendarDaySnapshot エンティティのテスト"""

    def test_create_basic_snapshot(self):
        """基本的なスナップショット作成のテスト"""
        snapshot = CalendarDaySnapshot(
            date="2024-12-01",
            has_meal_logs=True,
            nutrition_achievement=85,
            has_daily_report=True
        )

        assert snapshot.date == "2024-12-01"
        assert snapshot.has_meal_logs is True
        assert snapshot.nutrition_achievement == 85
        assert snapshot.has_daily_report is True

    def test_create_snapshot_no_nutrition_target(self):
        """栄養目標なしの場合のテスト"""
        snapshot = CalendarDaySnapshot(
            date="2024-12-02",
            has_meal_logs=False,
            nutrition_achievement=None,
            has_daily_report=False
        )

        assert snapshot.date == "2024-12-02"
        assert snapshot.has_meal_logs is False
        assert snapshot.nutrition_achievement is None
        assert snapshot.has_daily_report is False

    def test_snapshot_is_immutable(self):
        """スナップショットが不変オブジェクトであることのテスト"""
        snapshot = CalendarDaySnapshot(
            date="2024-12-03",
            has_meal_logs=True,
            nutrition_achievement=75,
            has_daily_report=True
        )

        # frozen=Trueなので属性変更はエラーになる
        with pytest.raises(AttributeError):
            snapshot.date = "2024-12-04"  # type: ignore

        with pytest.raises(AttributeError):
            snapshot.has_meal_logs = False  # type: ignore

    def test_snapshot_equality(self):
        """スナップショットの等価性テスト"""
        snapshot1 = CalendarDaySnapshot(
            date="2024-12-01",
            has_meal_logs=True,
            nutrition_achievement=85,
            has_daily_report=True
        )

        snapshot2 = CalendarDaySnapshot(
            date="2024-12-01",
            has_meal_logs=True,
            nutrition_achievement=85,
            has_daily_report=True
        )

        assert snapshot1 == snapshot2

        # 異なる値の場合は等しくない
        snapshot3 = CalendarDaySnapshot(
            date="2024-12-01",
            has_meal_logs=False,
            nutrition_achievement=85,
            has_daily_report=True
        )

        assert snapshot1 != snapshot3