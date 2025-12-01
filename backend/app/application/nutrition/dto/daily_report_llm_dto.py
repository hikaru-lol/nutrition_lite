from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List

from app.domain.auth.value_objects import UserId
from app.domain.profile.entities import Profile  # 実際のパスに合わせて調整
from app.domain.target.entities import DailyTargetSnapshot  # 実際のパスに合わせて調整
from app.domain.nutrition.daily_nutrition import DailyNutritionSummary
from app.domain.nutrition.meal_nutrition import MealNutritionSummary  # 名前は実装に合わせて


@dataclass
class DailyReportLLMInput:
    """
    日次レポート生成用の LLM 入力 DTO。

    - LLM に渡したい情報を 1 つの構造体にまとめる。
    """

    user_id: UserId
    date: date

    profile: Profile
    target_snapshot: DailyTargetSnapshot
    daily_summary: DailyNutritionSummary
    meal_summaries: List[MealNutritionSummary]


@dataclass
class DailyReportLLMOutput:
    """
    日次レポート生成用の LLM 出力 DTO。

    - LLM からはこの形で返ってくる前提でプロンプトを設計する。
    """

    summary: str
    good_points: List[str]
    improvement_points: List[str]
    tomorrow_focus: List[str]
