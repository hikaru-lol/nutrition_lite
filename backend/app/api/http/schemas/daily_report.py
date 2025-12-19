from __future__ import annotations

import datetime
from typing import List

from pydantic import BaseModel, Field


class GenerateDailyReportRequest(BaseModel):
    """
    日次レポート生成用のリクエストボディ。

    - date: 対象日 (YYYY-MM-DD)
    """
    date: datetime.date = Field(..., description="レポート対象日 (YYYY-MM-DD)")


class DailyNutritionReportResponse(BaseModel):
    """
    日次レポートのレスポンススキーマ。

    - 今回は基本的にドメインの DailyNutritionReport をそのまま API 用にマッピング。
    """

    date: datetime.date

    summary: str

    good_points: List[str]
    improvement_points: List[str]
    tomorrow_focus: List[str]
    created_at: datetime.datetime
