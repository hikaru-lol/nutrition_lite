# app/application/nutrition/dto/meal_recommendation_llm_dto.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_report import DailyNutritionReport
from app.application.profile.ports.profile_query_port import ProfileForTarget
# active_target はあとから足してもOK。まずは Profile + Reports だけで始める。


@dataclass(slots=True)
class MealRecommendationLLMInput:
    """
    MealRecommendation 用の LLM 入力 DTO。

    - base_date: この日までの履歴（通常「今日」）
    - recent_reports: 直近 N 日分の DailyNutritionReport
    """

    user_id: UserId
    base_date: date
    profile: ProfileForTarget
    recent_reports: list[DailyNutritionReport]


@dataclass(slots=True)
class MealRecommendationLLMOutput:
    """
    MealRecommendation 用の LLM 出力 DTO。
    """

    body: str
    tips: list[str]
