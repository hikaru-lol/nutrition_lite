from __future__ import annotations

from datetime import date as DateType

# === Third-party ============================================================
from fastapi import APIRouter, Depends, Query, HTTPException

# === API (schemas / dependencies) ==========================================
from app.api.http.dependencies.auth import get_current_user_dto
from app.api.http.schemas.nutrition import (
    DailyNutrientResponse,
    DailyNutritionSummaryResponse,
    MealAndDailyNutritionResponse,
    MealNutritionSummaryResponse,
    MealNutrientResponse,
)
from app.api.http.schemas.errors import ErrorResponse

# === Application (DTO / UseCase) ============================================
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.nutrition.use_cases.compute_daily_nutrition import (
    ComputeDailyNutritionSummaryUseCase,
)
from app.application.nutrition.use_cases.compute_meal_nutrition import (
    ComputeMealNutritionUseCase,
)
from app.application.nutrition.use_cases.get_meal_nutrition import (
    GetMealNutritionUseCase,
)
from app.application.nutrition.use_cases.get_daily_nutrition import (
    GetDailyNutritionUseCase,
)

# === Domain ================================================================
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_nutrition import DailyNutritionSummary
from app.domain.nutrition.meal_nutrition import MealNutritionSummary

# === DI =====================================================================
from app.di.container import (
    get_compute_daily_nutrition_summary_use_case,
    get_compute_meal_nutrition_use_case,
    get_get_daily_nutrition_use_case,
    get_get_meal_nutrition_use_case,
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
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
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
    get_meal_uc: GetMealNutritionUseCase = Depends(
        get_get_meal_nutrition_use_case
    ),
    get_daily_uc: GetDailyNutritionUseCase = Depends(
        get_get_daily_nutrition_use_case
    ),
) -> MealAndDailyNutritionResponse:
    """
    1回の食事（main/snack）について既存の栄養サマリを取得し、
    同じ日の 1日分の栄養サマリも同時に返す。

    OpenAI計算は行わず、DBに保存されているデータのみを返す。
    データが存在しない場合は404エラーを返す。

    フロー:
      1. GetMealNutritionUseCase → 既存データ取得のみ
      2. GetDailyNutritionUseCase → 既存データ取得のみ
      3. データなしの場合は404
      4. Meal + Daily をまとめて返す
    """

    user_id: UserId = UserId(current_user.id)

    # ① 1食分の既存栄養サマリを取得（OpenAI計算なし）
    meal_summary = get_meal_uc.execute(
        user_id=user_id,
        date_=date,
        meal_type_str=meal_type,
        meal_index=meal_index,
    )

    # ② 1日分の既存栄養サマリを取得（OpenAI計算なし）
    daily_summary = get_daily_uc.execute(
        user_id=user_id,
        date_=date,
    )

    # ③ データが存在しない場合は404
    if not meal_summary or not daily_summary:
        raise HTTPException(
            status_code=404,
            detail="Nutrition data not found. Use POST /nutrition/meal/compute to calculate."
        )

    # ④ Meal + Daily をまとめてレスポンス
    return MealAndDailyNutritionResponse(
        meal=_to_meal_response(meal_summary),
        daily=_to_daily_response(daily_summary),
    )


@router.post(
    "/nutrition/meal/compute",
    response_model=MealAndDailyNutritionResponse,
    status_code=201,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def compute_meal_and_daily_nutrition(
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
    compute_meal_uc: ComputeMealNutritionUseCase = Depends(
        get_compute_meal_nutrition_use_case
    ),
    compute_daily_uc: ComputeDailyNutritionSummaryUseCase = Depends(
        get_compute_daily_nutrition_summary_use_case
    ),
) -> MealAndDailyNutritionResponse:
    """
    1回の食事（main/snack）について栄養サマリをOpenAIで再計算し、
    その結果と、同じ日の 1日分の栄養サマリも同時に返す。

    このエンドポイントは明示的にOpenAI計算を実行します。
    既存データの有無に関わらず、常に再計算を行います。

    フロー:
      1. ComputeMealNutritionUseCase → OpenAI計算 & DB保存
      2. ComputeDailyNutritionSummaryUseCase → OpenAI計算 & DB保存
      3. Meal + Daily をまとめて返す
    """

    user_id: UserId = UserId(current_user.id)

    # ① 1食分の栄養サマリをOpenAIで再計算 & 保存
    meal_summary = compute_meal_uc.execute(
        user_id=user_id,
        date_=date,
        meal_type_str=meal_type,
        meal_index=meal_index,
    )

    # ② 1日分の栄養サマリをOpenAIで再計算 & 保存
    daily_summary = compute_daily_uc.execute(
        user_id=user_id,
        date_=date,
    )

    # ③ Meal + Daily をまとめてレスポンス
    return MealAndDailyNutritionResponse(
        meal=_to_meal_response(meal_summary),
        daily=_to_daily_response(daily_summary),
    )
