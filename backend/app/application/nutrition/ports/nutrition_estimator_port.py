from __future__ import annotations

from datetime import date
from typing import Protocol

from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.nutrition.meal_nutrition import MealNutrientIntake


class NutritionEstimatorPort(Protocol):
    """
    食事内容 (FoodEntry の集合) から栄養ベクトルを推定するためのポート。

    - 入力: あるユーザーの、ある日付に紐づく FoodEntry のリスト
    - 出力: その集合で摂取した栄養素ごとの一覧 (MealNutrientIntake のリスト)

    このポートを実装することで、以下のような実装を差し替え可能にする:

      - StubNutritionEstimator:
          簡易的な固定テーブル / 適当ロジックで栄養値を返す
      - LLMNutritionEstimator:
          LLM に FoodEntry の内容を渡して栄養推定する
      - FoodDbNutritionEstimator:
          外部の栄養データベース (USDA 等) を参照して計算する

    UseCase 側 (ComputeMealNutritionUseCase / ComputeDailyNutritionSummaryUseCase など) は
    「FoodEntry のリスト → MealNutrientIntake のリスト」という形だけを前提にする。
    """

    def estimate_for_entries(
        self,
        *,
        user_id: UserId,
        date: date,
        entries: list[FoodEntry],
    ) -> list[MealNutrientIntake]:
        """
        指定されたユーザー・日付・FoodEntry の集合に対して、
        栄養素ごとの摂取量一覧を推定して返す。

        - entries には main/snack 問わず任意の FoodEntry のリストを渡せる。
          1回の食事 (1 main/snack) のみを渡せば MealNutrition 用に、
          その日の全ての FoodEntry を渡せば DailyNutrition 用にも流用できる。
        - 戻り値のリスト内で code は一意であることが期待される。
        """
        ...
