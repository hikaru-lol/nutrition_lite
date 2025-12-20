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

    date: datetime.date = Field(..., description="レポート対象日 (YYYY-MM-DD)")

    summary: str = Field(..., description="1日全体の総評（本文）")

    good_points: List[str] = Field(..., description="良かった点")
    improvement_points: List[str] = Field(..., description="改善できそうな点")
    tomorrow_focus: List[str] = Field(..., description="明日意識したいこと・アクション")
    created_at: datetime.datetime = Field(..., description="レポート作成日時")
