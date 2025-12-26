from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

from app.application.nutrition.use_cases.get_daily_nutrition_report import (
    GetDailyNutritionReportUseCase,
)
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_report import DailyNutritionReport
from tests.unit.application.nutrition.fakes import (
    FakeNutritionUnitOfWork,
    FakeDailyNutritionReportRepository,
)

pytestmark = pytest.mark.unit


def _make_user_id() -> UserId:
    return UserId(str(uuid4()))


def test_get_daily_nutrition_report_success() -> None:
    """正常系: 日次レポート取得成功"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ
    daily_report_repo = FakeDailyNutritionReportRepository()
    nutrition_uow = FakeNutritionUnitOfWork(
        daily_report_repo=daily_report_repo)

    # 既存のレポートを作成
    existing_report = DailyNutritionReport.create(
        user_id=user_id,
        date=target_date,
        summary="テストレポート",
        good_points=["良い点1", "良い点2"],
        improvement_points=["改善点1"],
        tomorrow_focus=["明日の焦点1"],
        created_at=datetime.now(timezone.utc),
    )
    daily_report_repo.save(existing_report)

    # UseCase実行
    use_case = GetDailyNutritionReportUseCase(uow=nutrition_uow)

    result = use_case.execute(user_id=user_id, date_=target_date)

    # 検証
    assert result is not None
    assert result.user_id == user_id
    assert result.date == target_date
    assert result.summary == "テストレポート"
    assert len(result.good_points) == 2
    assert len(result.improvement_points) == 1
    assert len(result.tomorrow_focus) == 1


def test_get_daily_nutrition_report_not_found() -> None:
    """正常系: レポートが存在しない場合はNoneを返す"""
    user_id = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ（レポートなし）
    daily_report_repo = FakeDailyNutritionReportRepository()
    nutrition_uow = FakeNutritionUnitOfWork(
        daily_report_repo=daily_report_repo)

    # UseCase実行
    use_case = GetDailyNutritionReportUseCase(uow=nutrition_uow)

    result = use_case.execute(user_id=user_id, date_=target_date)

    # 検証: Noneが返される
    assert result is None


def test_get_daily_nutrition_report_different_user() -> None:
    """正常系: 異なるユーザーのレポートは取得できない"""
    user_id1 = _make_user_id()
    user_id2 = _make_user_id()
    target_date = date(2025, 11, 24)

    # セットアップ: user_id1のレポートを作成
    daily_report_repo = FakeDailyNutritionReportRepository()
    nutrition_uow = FakeNutritionUnitOfWork(
        daily_report_repo=daily_report_repo)

    existing_report = DailyNutritionReport.create(
        user_id=user_id1,
        date=target_date,
        summary="ユーザー1のレポート",
        good_points=[],
        improvement_points=[],
        tomorrow_focus=[],
        created_at=datetime.now(timezone.utc),
    )
    daily_report_repo.save(existing_report)

    # UseCase実行: user_id2で取得を試みる
    use_case = GetDailyNutritionReportUseCase(uow=nutrition_uow)

    result = use_case.execute(user_id=user_id2, date_=target_date)

    # 検証: Noneが返される
    assert result is None


def test_get_daily_nutrition_report_different_date() -> None:
    """正常系: 異なる日付のレポートは取得できない"""
    user_id = _make_user_id()
    target_date1 = date(2025, 11, 24)
    target_date2 = date(2025, 11, 25)

    # セットアップ: target_date1のレポートを作成
    daily_report_repo = FakeDailyNutritionReportRepository()
    nutrition_uow = FakeNutritionUnitOfWork(
        daily_report_repo=daily_report_repo)

    existing_report = DailyNutritionReport.create(
        user_id=user_id,
        date=target_date1,
        summary="11/24のレポート",
        good_points=[],
        improvement_points=[],
        tomorrow_focus=[],
        created_at=datetime.now(timezone.utc),
    )
    daily_report_repo.save(existing_report)

    # UseCase実行: target_date2で取得を試みる
    use_case = GetDailyNutritionReportUseCase(uow=nutrition_uow)

    result = use_case.execute(user_id=user_id, date_=target_date2)

    # 検証: Noneが返される
    assert result is None
