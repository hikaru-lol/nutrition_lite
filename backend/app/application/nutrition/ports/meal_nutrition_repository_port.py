from __future__ import annotations

from datetime import date
from typing import Protocol, Sequence

from app.domain.auth.value_objects import UserId
from app.domain.meal.value_objects import MealType
from app.domain.nutrition.meal_nutrition import MealNutritionSummary


class MealNutritionSummaryRepositoryPort(Protocol):
    """
    MealNutritionSummary の永続化・取得用の Port。
    """

    def get_by_user_date_meal(
        self,
        *,
        user_id: UserId,
        target_date: date,
        meal_type: MealType,
        meal_index: int | None,
    ) -> MealNutritionSummary | None:
        """
        指定したユーザー + 日付 + 食事スロットに対応するサマリを1件返す。
        なければ None。
        """
        ...

    def list_by_user_and_date(
        self,
        *,
        user_id: UserId,
        target_date: date,
    ) -> Sequence[MealNutritionSummary]:
        """
        指定したユーザーの、ある1日分の MealNutritionSummary 一覧を返す。

        - 将来の日次レポート生成等に利用する。
        """
        ...

    def save(self, summary: MealNutritionSummary) -> None:
        """
        MealNutritionSummary を保存する。

        - summary.id が既存レコードと一致する場合は update
        - なければ insert 相当として扱う
        """
        ...
