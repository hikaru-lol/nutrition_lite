from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol, runtime_checkable

from app.domain.auth.value_objects import UserId


@dataclass(slots=True)
class ProfileForTarget:
    """
    Target 生成に必要なプロフィール情報だけを抜き出したスナップショット。
    """

    sex: str | None          # 例: "male" / "female" / "other" など
    birthdate: date | None
    height_cm: float | None
    weight_kg: float | None


@runtime_checkable
class ProfileQueryPort(Protocol):
    """
    Target 側から Profile 情報を問い合わせるためのポート。

    実装は Profile の UseCase(GetMyProfileUseCase) や Repository を使ってよい。
    """

    def get_profile_for_target(self, user_id: UserId) -> ProfileForTarget | None:
        """
        user_id に紐づくプロフィール情報を返す。

        - プロフィールが存在しなければ None
        """
        ...
