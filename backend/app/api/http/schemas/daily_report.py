from __future__ import annotations

from datetime import date
from typing import List

from pydantic import BaseModel, Field


class GenerateDailyReportRequest(BaseModel):
    """
    日次レポート生成用のリクエストボディ。

    - date: 対象日 (YYYY-MM-DD)
    """
    date: date = Field(..., description="レポート対象日 (YYYY-MM-DD)")


class DailyNutritionReportResponse(BaseModel):
    """
    日次レポートのレスポンススキーマ。

    - 今回は基本的にドメインの DailyNutritionReport をそのまま API 用にマッピング。
    """

    date: date

    summary: str

    good_points: List[str]
    improvement_points: List[str]
    tomorrow_focus: List[str]
