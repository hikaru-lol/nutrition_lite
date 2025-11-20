from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Sex(str, Enum):
    """ユーザーの性別。"""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNDISCLOSED = "undisclosed"


@dataclass(frozen=True)
class HeightCm:
    """身長（cm）を表す値オブジェクト。"""

    value: float

    def __post_init__(self) -> None:
        # 身長として現実的な範囲にざっくり制限
        if not (0 < self.value < 300):
            raise ValueError(f"Invalid height: {self.value} cm")


@dataclass(frozen=True)
class WeightKg:
    """体重（kg）を表す値オブジェクト。"""

    value: float

    def __post_init__(self) -> None:
        # 体重として現実的な範囲にざっくり制限
        if not (0 < self.value < 500):
            raise ValueError(f"Invalid weight: {self.value} kg")


@dataclass(frozen=True)
class ProfileImageId:
    """
    プロフィール画像のストレージ上のID（オブジェクトキーなど）。

    例:
      - "profiles/{user_id}/avatar.jpg"
      - "profile-images/{uuid}.png"
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("ProfileImageId cannot be empty")
