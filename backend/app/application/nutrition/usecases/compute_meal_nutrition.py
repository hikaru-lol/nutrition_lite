from __future__ import annotations

from datetime import date as DateType, datetime

from app.application.meal.ports.food_entry_repository_port import (
    FoodEntryRepositoryPort,
)
from app.application.nutrition.ports.nutrition_estimator_port import (
    NutritionEstimatorPort,
)
from app.application.nutrition.ports.meal_nutrition_repository_port import (
    MealNutritionSummaryRepositoryPort,
)
from app.domain.auth.value_objects import UserId
from app.domain.meal.errors import InvalidMealTypeError, InvalidMealIndexError
from app.domain.meal.value_objects import MealType
from app.domain.nutrition.errors import NutritionEstimationFailedError
from app.domain.nutrition.meal_nutrition import (
    MealNutritionSummary,
    MealNutritionSummaryId,
)
from app.domain.target.value_objects import NutrientSource


class ComputeMealNutritionUseCase:
    """
    1回の食事（main/snack）に対する栄養サマリを計算し、DBに保存する UseCase。

    フロー:
      1. (user_id, date, meal_type, meal_index) に対応する FoodEntry を取得
      2. NutritionEstimatorPort で栄養ベクトルを推定
      3. 既存の MealNutritionSummary があれば ID を引き継いで再計算
      4. Repository.save(...) で upsert
      5. 最新の MealNutritionSummary を返す

    ※ 計算タイミングは「評価したい瞬間」（パターンB）を想定。
    """

    def __init__(
        self,
        food_entry_repo: FoodEntryRepositoryPort,
        meal_nutrition_repo: MealNutritionSummaryRepositoryPort,
        estimator: NutritionEstimatorPort,
    ) -> None:
        self._food_entry_repo = food_entry_repo
        self._meal_nutrition_repo = meal_nutrition_repo
        self._estimator = estimator

    def execute(
        self,
        user_id: UserId,
        date_: DateType,
        meal_type_str: str,
        meal_index: int | None,
    ) -> MealNutritionSummary:
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

        # --- 対象食事の FoodEntry 一覧を取得 --------------------------
        entries = list(
            self._food_entry_repo.list_by_user_date_type_index(
                user_id=user_id,
                target_date=date_,
                meal_type=meal_type,
                meal_index=meal_index,
            )
        )

        # --- 栄養推定 (Estimator) --------------------------------------
        try:
            nutrient_intakes = self._estimator.estimate_for_entries(
                user_id=user_id,
                date=date_,
                entries=entries,
            )
        except Exception as exc:
            # Estimator 内部の例外を NutritionEstimationFailedError にラップ
            raise NutritionEstimationFailedError(
                f"Failed to estimate nutrients for user={user_id.value}, date={date_}, "
                f"meal_type={meal_type.value}, meal_index={meal_index}: {exc}"
            ) from exc

        # --- 既存サマリの存在チェック ---------------------------------
        existing = self._meal_nutrition_repo.get_by_user_date_meal(
            user_id=user_id,
            target_date=date_,
            meal_type=meal_type,
            meal_index=meal_index,
        )

        # 由来: 今は「LLM などによる推定値」という扱いで "llm" を使う
        source = NutrientSource("llm")

        if existing is not None:
            summary_id: MealNutritionSummaryId | None = existing.id
        else:
            summary_id = None

        # --- MealNutritionSummary を組み立て --------------------------
        # Estimator が返した nutrient_intakes は List[MealNutrientIntake] なので、
        # code/amount を抜き出して from_nutrient_amounts を使っても良いし、
        # ここでそのまま生成しても良い。
        # ここでは from_nutrient_amounts を使うパターンを想定。
        pairs = [(n.code, n.amount) for n in nutrient_intakes]

        summary = MealNutritionSummary.from_nutrient_amounts(
            user_id=user_id,
            date=date_,
            meal_type=meal_type,
            meal_index=meal_index,
            nutrients=pairs,
            source=source,
            summary_id=summary_id,
        )

        # --- 保存 (upsert) --------------------------------------------
        self._meal_nutrition_repo.save(summary)

        return summary
