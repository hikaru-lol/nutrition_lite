from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List

from app.domain.auth.value_objects import UserId
from app.domain.profile.entities import Profile  # 実際のパスに合わせて調整
from app.domain.target.entities import TargetDefinition  # or DailyTargetSnapshot 等
from app.domain.nutrition.daily_report import DailyNutritionReport


@dataclass
class MealRecommendationLLMInput:
    """
    提案生成用 LLM 入力 DTO。

    - 基本は「直近 N 日分の日次レポート」を中心に構成。
    """

    user_id: UserId
    base_date: date  # この日までの履歴をもとに提案する、という基準日

    profile: Profile
    active_target: TargetDefinition | None  # なくても提案は可能として Optional にしておく

    recent_reports: List[DailyNutritionReport]  # 新しい順 or 古い順はプロンプト側で決める


@dataclass
class MealRecommendationLLMOutput:
    """
    提案生成用 LLM 出力 DTO。
    """

    body: str          # メインの提案文
    tips: List[str]    # 箇条書きのアクションポイントなど
