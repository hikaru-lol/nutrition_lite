from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from app.domain.auth.value_objects import UserId
from app.domain.meal.value_objects import FoodEntryId, MealType
from app.domain.meal.errors import InvalidMealIndexError, InvalidFoodAmountError


@dataclass
class FoodEntry:
    """
    1品分の食事ログ。

    - いつ（date）
    - 何回目の食事か（meal_type, meal_index）
    - 何をどれくらい食べたか（name, amount_value/amount_unit/serving_count）

    ※ meal_index と meals_per_day（Profileの情報）の整合性
       （例: meals_per_day=3 のユーザーが meal_index=5 を持たない）
       については Application 層の UseCase でチェックする想定。
    """

    id: FoodEntryId
    user_id: UserId

    date: date

    # 食事の種別: main（メインの食事）/ snack（間食）
    meal_type: MealType

    # メインの食事の何回目か（1回目/2回目/...）
    # - meal_type == main のとき: 1以上の整数
    # - meal_type == snack のとき: None
    meal_index: int | None

    # 内容
    name: str

    # 量指定（どちらか必須）
    amount_value: float | None  # 例: 150
    amount_unit: str | None     # 例: "g"
    serving_count: float | None  # 例: 1.5 (人前)

    note: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        self._validate_meal_index()
        self._validate_amount()

    # --- Validation -----------------------------------------------------

    def _validate_meal_index(self) -> None:
        """
        meal_type と meal_index の組み合わせチェック。

        - main なのに meal_index が None or 1 未満 → エラー
        - snack なのに meal_index が None 以外 → エラー
        """
        if self.meal_type == MealType.MAIN:
            if self.meal_index is None or self.meal_index < 1:
                raise InvalidMealIndexError(
                    f"MealType=main の場合、meal_index は 1 以上の整数が必要です: {self.meal_index}"
                )
        elif self.meal_type == MealType.SNACK:
            if self.meal_index is not None:
                raise InvalidMealIndexError(
                    f"MealType=snack の場合、meal_index は None である必要があります: {self.meal_index}"
                )

    def _validate_amount(self) -> None:
        """
        量指定のチェック。

        - 「amount_value + amount_unit」か「serving_count」のどちらか必須
        - amount_value があるなら > 0 & amount_unit も必須
        - serving_count があるなら > 0
        """
        has_value_pair = self.amount_value is not None or self.amount_unit is not None
        has_serving = self.serving_count is not None

        # どちらも指定されていない場合は NG
        if not has_value_pair and not has_serving:
            raise InvalidFoodAmountError(
                "amount_value/amount_unit または serving_count のいずれかは必須です"
            )

        # amount_value / amount_unit の組み合わせチェック
        if self.amount_value is not None or self.amount_unit is not None:
            if self.amount_value is None or self.amount_unit is None:
                raise InvalidFoodAmountError(
                    "amount_value と amount_unit は両方指定する必要があります"
                )
            if self.amount_value <= 0:
                raise InvalidFoodAmountError(
                    f"amount_value は 0 より大きい値が必要です: {self.amount_value}"
                )

        # serving_count のチェック
        if self.serving_count is not None:
            if self.serving_count <= 0:
                raise InvalidFoodAmountError(
                    f"serving_count は 0 より大きい値が必要です: {self.serving_count}"
                )
