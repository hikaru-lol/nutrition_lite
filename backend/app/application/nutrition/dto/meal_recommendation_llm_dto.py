from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_report import DailyNutritionReport
from app.application.profile.ports.profile_query_port import ProfileForRecommendation


@dataclass(slots=True, frozen=True)
class RecommendedMealDTO:
    """推奨献立のDTO"""
    title: str
    description: str
    ingredients: list[str]
    nutrition_focus: str


@dataclass(slots=True)
class MealRecommendationLLMInput:
    user_id: UserId
    base_date: date               # この日までの履歴（通常「今日」）
    profile: ProfileForRecommendation
    recent_reports: list[DailyNutritionReport]


@dataclass(slots=True)
class MealRecommendationLLMOutput:
    body: str
    tips: list[str]
    recommended_meals: list[RecommendedMealDTO]
