from __future__ import annotations

from datetime import date as DateType

# === Third-party ============================================================
from fastapi import APIRouter, Depends, Query

# === API (schemas / dependencies) ==========================================
from app.api.http.dependencies.auth import get_current_user_dto
from app.api.http.schemas.nutrition import (
    DailyNutrientResponse,
    DailyNutritionSummaryResponse,
    MealAndDailyNutritionResponse,
    MealNutritionSummaryResponse,
    MealNutrientResponse,
)

# === Application (DTO / UseCase) ============================================
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.nutrition.use_cases.compute_daily_nutrition import (
    ComputeDailyNutritionSummaryUseCase,
)
from app.application.nutrition.use_cases.compute_meal_nutrition import (
    ComputeMealNutritionUseCase,
)

# === Domain ================================================================
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_nutrition import DailyNutritionSummary
from app.domain.nutrition.meal_nutrition import MealNutritionSummary

# === DI =====================================================================
from app.di.container import (
    get_compute_daily_nutrition_summary_use_case,
    get_compute_meal_nutrition_use_case,
)


router = APIRouter(tags=["Nutrition"])


# === Helpers ===============================================================


def _to_meal_response(summary: MealNutritionSummary) -> MealNutritionSummaryResponse:
    """
    Domain の MealNutritionSummary -> API レスポンスへの変換。
    """
    return MealNutritionSummaryResponse(
        id=str(summary.id.value),
        date=summary.date,
        meal_type=summary.meal_type.value,
        meal_index=summary.meal_index,
        generated_at=summary.generated_at,
        nutrients=[
            MealNutrientResponse(
                code=n.code.value,
                value=n.amount.value,
                unit=n.amount.unit,
                source=n.source.value,
            )
            for n in summary.nutrients
        ],
    )


def _to_daily_response(summary: DailyNutritionSummary) -> DailyNutritionSummaryResponse:
    """
    Domain の DailyNutritionSummary -> API レスポンスへの変換。
    """
    return DailyNutritionSummaryResponse(
        id=str(summary.id.value),
        date=summary.date,
        generated_at=summary.generated_at,
        nutrients=[
            DailyNutrientResponse(
                code=n.code.value,
                value=n.amount.value,
                unit=n.amount.unit,
                source=n.source.value,
            )
            for n in summary.nutrients
        ],
    )


# === Routes ================================================================


@router.get(
    "/nutrition/meal",
    response_model=MealAndDailyNutritionResponse,
)
def get_meal_and_daily_nutrition(
    date: DateType = Query(..., description="対象日 (YYYY-MM-DD)"),
    meal_type: str = Query(
        ...,
        description='"main" または "snack"',
        regex="^(main|snack)$",
    ),
    meal_index: int | None = Query(
        default=None,
        description=(
            "meal_type == main のとき: 1..N / "
            "meal_type == snack のとき: null"
        ),
    ),
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    meal_uc: ComputeMealNutritionUseCase = Depends(
        get_compute_meal_nutrition_use_case
    ),
    daily_uc: ComputeDailyNutritionSummaryUseCase = Depends(
        get_compute_daily_nutrition_summary_use_case
    ),
) -> MealAndDailyNutritionResponse:
    """
    1回の食事（main/snack）について栄養サマリを再計算し、
    その結果と、同じ日の 1日分の栄養サマリも同時に返す。

    フロー:
      1. ComputeMealNutritionUseCase
         → MealNutritionSummary を再計算 & 保存
      2. ComputeDailyNutritionSummaryUseCase
         → その日付の DailyNutritionSummary を再計算 & 保存
      3. Meal + Daily をまとめて返す
    """

    user_id: UserId = current_user.id

    # ① 1食分の栄養サマリを再計算 & 保存
    meal_summary = meal_uc.execute(
        user_id=user_id,
        date_=date,
        meal_type_str=meal_type,
        meal_index=meal_index,
    )

    # ② 1日分の栄養サマリを再計算 & 保存
    daily_summary = daily_uc.execute(
        user_id=user_id,
        date_=date,
    )

    # ③ Meal + Daily をまとめてレスポンス
    return MealAndDailyNutritionResponse(
        meal=_to_meal_response(meal_summary),
        daily=_to_daily_response(daily_summary),
    )
