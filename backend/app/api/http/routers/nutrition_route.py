from __future__ import annotations

from datetime import date as DateType

from fastapi import APIRouter, Depends, Query

from app.api.http.schemas.nutrition import (
    MealNutritionSummaryResponse,
    MealType,
    MealNutrientResponse,
)
from app.api.http.dependencies.auth import get_current_user_dto
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.nutrition.use_cases.compute_meal_nutrition import (
    ComputeMealNutritionUseCase,
)
from app.di.container import get_compute_meal_nutrition_use_case
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.meal_nutrition import MealNutritionSummary

router = APIRouter(tags=["Nutrition"])


def _to_response_dto(summary: MealNutritionSummary) -> MealNutritionSummaryResponse:
    """
    Domain の MealNutritionSummary -> API Response 変換。
    """
    return MealNutritionSummaryResponse(
        id=str(summary.id.value),
        date=summary.date,
        meal_type=MealType(summary.meal_type.value),
        meal_index=summary.meal_index,
        generated_at=summary.generated_at,
        nutrients=[
            MealNutrientResponse(
                code=MealNutrientResponse.model_fields[
                    "code"].annotation(n.code.value),
                value=n.amount.value,
                unit=n.amount.unit,
                source=n.source.value,
            )
            for n in summary.nutrients
        ],
    )


@router.get(
    "/nutrition/meal",
    response_model=MealNutritionSummaryResponse,
)
def get_meal_nutrition_summary(
    date: DateType = Query(..., description="対象日 (YYYY-MM-DD)"),
    meal_type: MealType = Query(..., description='"main" または "snack"'),
    meal_index: int | None = Query(
        default=None,
        description="meal_type == main のとき: 1..N / meal_type == snack のとき: null",
    ),
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: ComputeMealNutritionUseCase = Depends(
        get_compute_meal_nutrition_use_case
    ),
) -> MealNutritionSummaryResponse:
    """
    1回の食事（main/snack）に対する栄養サマリを計算し、DBに保存して返す。

    - 計算タイミングは「評価を見たいとき」（パターンB）
    - すでにサマリがある場合は再計算して上書き保存
    """

    user_id: UserId = current_user.user_id

    summary = use_case.execute(
        user_id=user_id,
        date_=date,
        meal_type_str=meal_type.value,
        meal_index=meal_index,
    )

    return _to_response_dto(summary)
