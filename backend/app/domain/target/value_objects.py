from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class GoalType(str, Enum):
    """ターゲットの目的種別。"""

    WEIGHT_LOSS = "weight_loss"
    MAINTAIN = "maintain"
    WEIGHT_GAIN = "weight_gain"
    HEALTH_IMPROVE = "health_improve"

    def __str__(self) -> str:
        return self.value


class ActivityLevel(str, Enum):
    """運動量のレベル。ターゲット計算時に使用する。"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

    def __str__(self) -> str:
        return self.value


class NutrientCode(str, Enum):
    """1日あたりのターゲットを持つ 17 種類の栄養素コード。"""

    # エネルギー源
    CARBOHYDRATE = "carbohydrate"
    FAT = "fat"
    PROTEIN = "protein"

    # ビタミン
    VITAMIN_A = "vitamin_a"
    VITAMIN_B_COMPLEX = "vitamin_b_complex"
    VITAMIN_C = "vitamin_c"
    VITAMIN_D = "vitamin_d"
    VITAMIN_E = "vitamin_e"
    VITAMIN_K = "vitamin_k"

    # ミネラル
    CALCIUM = "calcium"
    IRON = "iron"
    MAGNESIUM = "magnesium"
    ZINC = "zinc"
    SODIUM = "sodium"
    POTASSIUM = "potassium"

    # その他
    FIBER = "fiber"
    WATER = "water"

    def __str__(self) -> str:
        return self.value


NutrientSourceLiteral = Literal["llm", "manual", "user_input"]


@dataclass(frozen=True)
class TargetId:
    """ターゲット定義を一意に識別する ID。"""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("TargetId cannot be empty")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class NutrientAmount:
    """
    栄養素の目標量 + 単位。

    例:
      - 150.0 g
      - 10.0 mg
      - 2000.0 kcal
    """

    value: float
    unit: str

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Nutrient amount cannot be negative")
        if not self.unit:
            raise ValueError("Nutrient unit cannot be empty")

    def __str__(self) -> str:
        return f"{self.value} {self.unit}"


@dataclass(frozen=True)
class NutrientSource:
    """
    ターゲット値の由来。

    - "llm"       : LLM による自動推定値
    - "manual"    : ユーザーによる手動変更後の値
    - "user_input": ユーザーが直接入力した値（サプリ等）
    """

    value: NutrientSourceLiteral

    def __post_init__(self) -> None:
        if self.value not in ("llm", "manual", "user_input"):
            raise ValueError(f"Invalid nutrient source: {self.value}")

    def __str__(self) -> str:
        return self.value
