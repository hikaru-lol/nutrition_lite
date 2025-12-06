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
    """
    1日あたりのターゲットを持つ 10 種類の栄養素コード。

    - carbohydrate : 炭水化物 (g)
    - fat          : 脂質 (g)
    - protein      : たんぱく質 (g)
    - water        : 水分 (ml)
    - fiber        : 食物繊維 (g)
    - sodium       : ナトリウム (mg)
    - iron         : 鉄 (mg)
    - calcium      : カルシウム (mg)
    - vitamin_d    : ビタミンD (µg)
    - potassium    : カリウム (mg)
    """

    CARBOHYDRATE = "carbohydrate"
    FAT = "fat"
    PROTEIN = "protein"
    WATER = "water"
    FIBER = "fiber"
    SODIUM = "sodium"
    IRON = "iron"
    CALCIUM = "calcium"
    VITAMIN_D = "vitamin_d"
    POTASSIUM = "potassium"

    def __str__(self) -> str:
        return self.value


# このアプリで扱う全栄養素コード（10種類）
ALL_NUTRIENT_CODES: tuple[NutrientCode, ...] = (
    NutrientCode.CARBOHYDRATE,
    NutrientCode.FAT,
    NutrientCode.PROTEIN,
    NutrientCode.WATER,
    NutrientCode.FIBER,
    NutrientCode.SODIUM,
    NutrientCode.IRON,
    NutrientCode.CALCIUM,
    NutrientCode.VITAMIN_D,
    NutrientCode.POTASSIUM,
)

# 各栄養素のデフォルト単位
DEFAULT_NUTRIENT_UNITS: dict[NutrientCode, str] = {
    NutrientCode.CARBOHYDRATE: "g",
    NutrientCode.FAT: "g",
    NutrientCode.PROTEIN: "g",
    NutrientCode.WATER: "ml",
    NutrientCode.FIBER: "g",
    NutrientCode.SODIUM: "mg",
    NutrientCode.IRON: "mg",
    NutrientCode.CALCIUM: "mg",
    NutrientCode.VITAMIN_D: "µg",
    NutrientCode.POTASSIUM: "mg",
}


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
