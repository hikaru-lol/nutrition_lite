from __future__ import annotations

from datetime import date as DateType

from app.application.nutrition.ports.uow_port import NutritionUnitOfWorkPort
from app.application.auth.ports.plan_checker_port import PlanCheckerPort

from app.domain.auth.value_objects import UserId
from app.domain.meal.value_objects import MealType
from app.domain.meal.errors import InvalidMealTypeError, InvalidMealIndexError
from app.domain.nutrition.meal_nutrition import MealNutritionSummary


class GetMealNutritionUseCase:
    """
    1回の食事（main/snack）に対する既存の栄養サマリを取得するUseCase。

    OpenAI計算は行わず、DBに保存されているデータのみを返す。
    データが存在しない場合はNoneを返す。

    フロー:
      1. (user_id, date, meal_type, meal_index) に対応する既存データを検索
      2. 見つかればそのまま返す、なければNone
    """

    def __init__(
        self,
        nutrition_uow: NutritionUnitOfWorkPort,
        plan_checker: PlanCheckerPort,
    ) -> None:
        self._nutrition_uow = nutrition_uow
        self._plan_checker = plan_checker

    def execute(
        self,
        user_id: UserId,
        date_: DateType,
        meal_type_str: str,
        meal_index: int | None,
    ) -> MealNutritionSummary | None:
        # --- 0. プレミアム機能チェック --------------------------------
        self._plan_checker.ensure_premium_feature(user_id)

        # --- meal_type の文字列 → Enum 変換 ----------------------------
        try:
            meal_type = MealType(meal_type_str)
        except ValueError:
            raise InvalidMealTypeError(f"Invalid meal_type: {meal_type_str}")

        # meal_type と meal_index の整合性チェック
        if meal_type == MealType.MAIN:
            if meal_index is None or meal_index < 1:
                raise InvalidMealIndexError(
                    f"MealType=main の場合、meal_index は 1 以上の整数が必要です: {meal_index}"
                )
        else:  # SNACK
            if meal_index is not None:
                raise InvalidMealIndexError(
                    f"MealType=snack の場合、meal_index は None である必要があります: {meal_index}"
                )

        # 既存データの検索のみ（OpenAI計算なし）
        with self._nutrition_uow as uow:
            existing = uow.meal_nutrition_repo.get_by_user_date_meal(
                user_id=user_id,
                target_date=date_,
                meal_type=meal_type,
                meal_index=meal_index,
            )

            if existing:
                existing.ensure_full_nutrients()

            return existing