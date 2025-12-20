from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol, runtime_checkable

from app.domain.auth.value_objects import UserId
from app.domain.profile.value_objects import Sex, HeightCm, WeightKg

# 既存


@dataclass(slots=True)
class ProfileForTarget:
    sex: str | None
    birthdate: date | None
    height_cm: float | None
    weight_kg: float | None


@dataclass(slots=True)
class ProfileForDailyLog:
    sex: Sex
    birthdate: date
    height_cm: HeightCm
    weight_kg: WeightKg
    meals_per_day: int | None = None


# ★ 追加: Recommendation 用 DTO ----------------------------------------

@dataclass(slots=True)
class ProfileForRecommendation:
    """
    MealRecommendation 用に参照したいプロフィール情報のスナップショット。

    - sex / birthdate / height / weight: おおまかな体格・属性
    - meals_per_day: 1日の食事回数（提案に反映しやすい）
    """
    sex: str | None
    birthdate: date | None
    height_cm: float | None
    weight_kg: float | None
    meals_per_day: int | None


@runtime_checkable
class ProfileQueryPort(Protocol):
    """
    他コンテキスト(Target / Meal / Nutrition / Recommendation 等) から
    Profile 情報を用途別の形で問い合わせるためのポート。
    """

    # --- Target 用 -----------------------------------------------------

    def get_profile_for_target(self, user_id: UserId) -> ProfileForTarget | None:
        ...

    # --- DailyLog 用 ---------------------------------------------------

    def get_profile_for_daily_log(self, user_id: UserId) -> ProfileForDailyLog | None:
        ...

    # --- Recommendation 用 --------------------------------------------

    def get_profile_for_recommendation(
        self, user_id: UserId
    ) -> ProfileForRecommendation | None:
        """
        MealRecommendation 生成に必要なプロフィール情報を返す。

        - プロフィールが存在しなければ None
        """
        ...
