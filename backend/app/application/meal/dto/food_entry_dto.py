from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class CreateFoodEntryInputDTO:
    """
    FoodEntry 作成用の入力 DTO。

    - meal_type: "main" または "snack"
    - meal_index:
        - main のとき: 1..meals_per_day の整数（1回目/2回目/...）
        - snack のとき: None
    - 量指定:
        - amount_value + amount_unit
        - または serving_count
        のどちらかは必須（ドメイン側で検証）
    """

    date: date
    meal_type: str          # "main" | "snack"
    meal_index: int | None  # main のとき 1..N, snack のとき None

    name: str

    amount_value: float | None
    amount_unit: str | None
    serving_count: float | None

    note: str | None = None


@dataclass
class UpdateFoodEntryInputDTO:
    """
    FoodEntry 更新用の入力 DTO。

    いったん「フル更新」前提で、全フィールド必須。
    必要になったら部分更新用 DTO を切る。
    """

    entry_id: str           # UUID 文字列

    date: date
    meal_type: str
    meal_index: int | None

    name: str

    amount_value: float | None
    amount_unit: str | None
    serving_count: float | None

    note: str | None = None


@dataclass
class FoodEntryDTO:
    """
    API レスポンスなどで使いやすい形。
    """

    id: str

    date: date
    meal_type: str
    meal_index: int | None

    name: str

    amount_value: float | None
    amount_unit: str | None
    serving_count: float | None

    note: str | None


@dataclass
class UpdateFoodEntryResultDTO:
    """
    FoodEntry 更新結果 + 変更前の日付。

    - entry: 更新後の FoodEntryDTO
    - old_date: 更新前の date
    """
    entry: FoodEntryDTO
    old_date: date


@dataclass
class DeleteFoodEntryResultDTO:
    """
    FoodEntry 削除結果。

    - date: 削除されたエントリが属していた日付
    """
    date: date
