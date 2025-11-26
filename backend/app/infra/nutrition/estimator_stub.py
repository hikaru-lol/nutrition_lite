from __future__ import annotations

from datetime import date

from app.application.nutrition.ports.nutrition_estimator_port import (
    NutritionEstimatorPort,
)
from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.nutrition.meal_nutrition import MealNutrientIntake
from app.domain.target.value_objects import (
    NutrientCode,
    NutrientAmount,
    NutrientSource,
)


class StubNutritionEstimator(NutritionEstimatorPort):
    """
    超ざっくりな Stub 実装。

    目的:
      - 「FoodEntry → MealNutrientIntake[]」の線を通すこと
      - 正確な栄養値ではなく、「計算＆見せ方」の“計算”の土台を作ること

    ポリシー（仮）:
      - FoodEntry.amount_value を g とみなす
      - 100g あたりのざっくり係数で P/F/C を決める
      - 他の栄養素は 0 のまま（必要になったら拡張）
    """

    def estimate_for_entries(
        self,
        *,
        user_id: UserId,  # noqa: ARG002 (今は使用しないがインターフェース上残しておく)
        date: date,       # noqa: ARG002
        entries: list[FoodEntry],
    ) -> list[MealNutrientIntake]:
        # とりあえず PROTEIN / FAT / CARBOHYDRATE の3つだけ合計する例
        totals: dict[NutrientCode, float] = {
            NutrientCode.PROTEIN: 0.0,
            NutrientCode.FAT: 0.0,
            NutrientCode.CARBOHYDRATE: 0.0,
        }

        for e in entries:
            # 本来は name / amount_unit / serving_count 等も考慮すべきだが、
            # Stub なので「amount_value (g) × 適当な係数」で決めてしまう。
            base = e.amount_value or 0.0  # None の場合は 0 として扱う

            # ここでは「高タンパク寄り」など適当な係数を決めているだけ
            totals[NutrientCode.PROTEIN] += base * 0.20  # 20% がタンパク質
            totals[NutrientCode.FAT] += base * 0.10      # 10% が脂質
            totals[NutrientCode.CARBOHYDRATE] += base * 0.50  # 50% が炭水化物

        # 由来は「LLM などによる推定値」という扱いで "llm" を使う
        source = NutrientSource("llm")

        nutrients: list[MealNutrientIntake] = []

        for code, value in totals.items():
            # 今は全部 g 単位で返す（後で kcal 等に拡張してもよい）
            amount = NutrientAmount(value=value, unit="g")
            nutrients.append(
                MealNutrientIntake(
                    code=code,
                    amount=amount,
                    source=source,
                )
            )

        return nutrients
