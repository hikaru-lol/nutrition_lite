from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol, runtime_checkable

from app.domain.auth.value_objects import UserId


# --- Target 用 DTO ---------------------------------------------------------

@dataclass(slots=True)
class ProfileForTarget:
    """
    Target 生成に必要なプロフィール情報だけを抜き出したスナップショット。
    """

    sex: str | None          # 例: "male" / "female" / "other" など
    birthdate: date | None
    height_cm: float | None
    weight_kg: float | None


# --- DailyLog 用 DTO -------------------------------------------------------

@dataclass(slots=True)
class ProfileForDailyLog:
    """
    日次ログ判定に必要なプロフィール情報だけを抜き出したスナップショット。
    """

    meals_per_day: int | None


@runtime_checkable
class ProfileQueryPort(Protocol):
    """
    他コンテキスト(Target / Meal / Nutrition など) から
    Profile 情報を問い合わせるためのポート。

    実装は Profile の UseCase(GetMyProfileUseCase) や Repository を使ってよい。
    """

    # --- Target 用 ---------------------------------------------------------

    def get_profile_for_target(self, user_id: UserId) -> ProfileForTarget | None:
        """
        Target 生成に必要なプロフィール情報を返す。

        - プロフィールが存在しなければ None
        """
        ...

    # --- DailyLog 用 -------------------------------------------------------

    def get_profile_for_daily_log(self, user_id: UserId) -> ProfileForDailyLog | None:
        """
        日次ログ判定に必要なプロフィール情報を返す。

        - プロフィールが存在しなければ None
        """
        ...
