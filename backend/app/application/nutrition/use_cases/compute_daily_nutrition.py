from __future__ import annotations

from collections import defaultdict
from datetime import date as DateType

from app.application.nutrition.ports.daily_nutrition_repository_port import (
    DailyNutritionSummaryRepositoryPort,
)
from app.application.nutrition.ports.meal_nutrition_repository_port import (
    MealNutritionSummaryRepositoryPort,
)
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_nutrition import (
    DailyNutritionSummary,
    DailyNutritionSummaryId,
)
from app.domain.target.value_objects import NutrientCode, NutrientAmount, NutrientSource


class ComputeDailyNutritionSummaryUseCase:
    """
    1日分の栄養サマリ (DailyNutritionSummary) を計算し、DB に保存する UseCase。

    - 入力:
        user_id, date
    - 処理:
        1. その日の MealNutritionSummary 一覧を取得
        2. NutrientCode ごとに amount.value を合計
        3. DailyNutritionSummary を組み立て
        4. 既存サマリがあれば上書き、なければ新規作成
    - 出力:
        最新の DailyNutritionSummary
    """

    def __init__(
        self,
        meal_repo: MealNutritionSummaryRepositoryPort,
        daily_repo: DailyNutritionSummaryRepositoryPort,
    ) -> None:
        self._meal_repo = meal_repo
        self._daily_repo = daily_repo

    def execute(
        self,
        user_id: UserId,
        date_: DateType,
    ) -> DailyNutritionSummary:
        # --- 1. その日の Meal サマリ一覧を取得 ------------------------
        meals = self._meal_repo.list_by_user_and_date(
            user_id=user_id,
            target_date=date_,
        )

        # --- 2. NutrientCode ごとに合計 ------------------------------
        totals: dict[NutrientCode, float] = defaultdict(float)
        unit_map: dict[NutrientCode, str] = {}

        for meal in meals:
            for n in meal.nutrients:
                totals[n.code] += n.amount.value
                # 単位は基本同じ前提で、最初に出てきたものを採用
                unit_map.setdefault(n.code, n.amount.unit)

        # NutrientCode -> NutrientAmount のペアリストに変換
        pairs: list[tuple[NutrientCode, NutrientAmount]] = [
            (code, NutrientAmount(value=value, unit=unit_map[code]))
            for code, value in totals.items()
        ]

        # --- 3. 既存サマリ (user_id, date) の有無を確認 ---------------
        existing = self._daily_repo.get_by_user_and_date(
            user_id=user_id,
            target_date=date_,
        )
        summary_id: DailyNutritionSummaryId | None = (
            existing.id if existing is not None else None
        )

        # 由来: MealNutritionSummary（多くは LLM 等で推定）から集計した合計という意味で "llm" を利用
        source = NutrientSource("llm")

        # --- 4. DailyNutritionSummary を組み立て ----------------------
        summary = DailyNutritionSummary.from_nutrient_amounts(
            user_id=user_id,
            date=date_,
            nutrients=pairs,
            source=source,
            summary_id=summary_id,
        )

        # --- 5. 保存 (upsert) -----------------------------------------
        self._daily_repo.save(summary)

        return summary
