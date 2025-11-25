from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID, uuid4


class MealType(str, Enum):
    """
    食事の種別。

    - main: メインの食事（1回目/2回目/…）
    - snack: 間食
    """

    MAIN = "main"
    SNACK = "snack"


@dataclass(frozen=True)
class FoodEntryId:
    """
    FoodEntry の ID（UUID をラップした ValueObject）。
    """

    value: UUID

    @classmethod
    def new(cls) -> FoodEntryId:
        return cls(uuid4())

    def __str__(self) -> str:  # 例: ログやAPIでの文字列表現
        return str(self.value)
