from __future__ import annotations

from datetime import date as DateType

from app.api.http.schemas.errors import ErrorResponse

# === Third-party ============================================================
from fastapi import APIRouter, Depends, Path, Query, Response, status

# === API (schemas / dependencies) ==========================================
from app.api.http.dependencies.auth import get_current_user_dto
from app.api.http.schemas.meal import (
    MealItemListResponse,
    MealItemRequest,
    MealItemResponse,
)

# === Domain ================================================================
from app.domain.auth.value_objects import UserId

# === Application (DTO / UseCase) ===========================================
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.meal.dto.food_entry_dto import (
    CreateFoodEntryInputDTO,
    FoodEntryDTO,
    UpdateFoodEntryInputDTO,
)
from app.application.meal.use_cases.create_food_entry import CreateFoodEntryUseCase
from app.application.meal.use_cases.delete_food_entry import DeleteFoodEntryUseCase
from app.application.meal.use_cases.list_food_entries_by_date import (
    ListFoodEntriesByDateUseCase,
)
from app.application.meal.use_cases.update_food_entry import UpdateFoodEntryUseCase
from app.application.nutrition.use_cases.compute_daily_nutrition import (
    ComputeDailyNutritionSummaryUseCase,
)

# === DI =====================================================================
from app.di.container import (
    get_compute_daily_nutrition_summary_use_case,
    get_create_food_entry_use_case,
    get_delete_food_entry_use_case,
    get_list_food_entries_by_date_use_case,
    get_update_food_entry_use_case,
)

router = APIRouter(tags=["Meal"])


# === Helpers ===============================================================


def _dto_to_response(dto: FoodEntryDTO) -> MealItemResponse:
    """
    Application の FoodEntryDTO -> API Response スキーマ変換。
    """
    return MealItemResponse(
        id=dto.id,
        date=dto.date,
        meal_type=dto.meal_type,
        meal_index=dto.meal_index,
        name=dto.name,
        amount_value=dto.amount_value,
        amount_unit=dto.amount_unit,
        serving_count=dto.serving_count,
        note=dto.note,
    )


def _recompute_daily_summaries(
    *,
    compute_daily_uc: ComputeDailyNutritionSummaryUseCase,
    user_id: str,
    dates: set[DateType],
) -> None:
    """
    影響のある日付の DailyNutritionSummary を再計算する共通処理。
    """
    for d in dates:
        compute_daily_uc.execute(
            user_id=user_id,
            date_=d,
        )


# === Routes ================================================================


@router.post(
    "/meal-items",
    response_model=MealItemResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
    },
)
def create_meal_item(
    request: MealItemRequest,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: CreateFoodEntryUseCase = Depends(get_create_food_entry_use_case),
) -> MealItemResponse:
    """
    FoodEntry（1品の食事ログ）を新規作成する。
    """

    input_dto = CreateFoodEntryInputDTO(
        date=request.date,
        meal_type=request.meal_type.value,  # Enum -> str ("main" / "snack")
        meal_index=request.meal_index,
        name=request.name,
        amount_value=request.amount_value,
        amount_unit=request.amount_unit,
        serving_count=request.serving_count,
        note=request.note,
    )

    dto = use_case.execute(UserId(current_user.id), input_dto)
    return _dto_to_response(dto)


@router.get(
    "/meal-items",
    response_model=MealItemListResponse,
    responses={
        401: {"model": ErrorResponse},
    },
)
def list_meal_items_by_date(
    date: DateType = Query(..., description="対象日 (YYYY-MM-DD)"),
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: ListFoodEntriesByDateUseCase = Depends(
        get_list_food_entries_by_date_use_case
    ),
) -> MealItemListResponse:
    """
    指定した 1 日分の FoodEntry 一覧を取得する。
    main / snack を区別せず、その日の全ての FoodEntry を返す。
    """

    dtos = use_case.execute(current_user.id, date)
    items = [_dto_to_response(dto) for dto in dtos]
    return MealItemListResponse(items=items)


@router.patch(
    "/meal-items/{entry_id}",
    response_model=MealItemResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def update_meal_item(
    request: MealItemRequest,
    entry_id: str = Path(..., description="FoodEntry ID (UUID 文字列)"),
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: UpdateFoodEntryUseCase = Depends(get_update_food_entry_use_case),
    compute_daily_uc: ComputeDailyNutritionSummaryUseCase = Depends(
        get_compute_daily_nutrition_summary_use_case
    ),
) -> MealItemResponse:
    """
    既存の FoodEntry を更新し、
    影響のある日の DailyNutritionSummary を再計算する。
    """

    input_dto = UpdateFoodEntryInputDTO(
        entry_id=entry_id,
        date=request.date,
        meal_type=request.meal_type.value,  # Enum -> str ("main" / "snack")
        meal_index=request.meal_index,
        name=request.name,
        amount_value=request.amount_value,
        amount_unit=request.amount_unit,
        serving_count=request.serving_count,
        note=request.note,
    )

    # UpdateFoodEntryUseCase は UpdateFoodEntryResultDTO を返す想定
    result = use_case.execute(current_user.id, input_dto)
    dto = result.entry

    # 影響する日付 = {更新前の日, 更新後の日}
    impacted_dates = {result.old_date, dto.date}
    _recompute_daily_summaries(
        compute_daily_uc=compute_daily_uc,
        user_id=current_user.id,
        dates=impacted_dates,
    )

    return _dto_to_response(dto)


@router.delete(
    "/meal-items/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def delete_meal_item(
    entry_id: str = Path(..., description="FoodEntry ID (UUID 文字列)"),
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: DeleteFoodEntryUseCase = Depends(get_delete_food_entry_use_case),
    compute_daily_uc: ComputeDailyNutritionSummaryUseCase = Depends(
        get_compute_daily_nutrition_summary_use_case
    ),
) -> Response:
    """
    FoodEntry を削除し、その日の DailyNutritionSummary を再計算する。

    - Repository 実装側ではソフトデリートを想定。
    """

    # DeleteFoodEntryUseCase は DeleteFoodEntryResultDTO を返す想定
    result = use_case.execute(current_user.id, entry_id)

    if result is not None:
        _recompute_daily_summaries(
            compute_daily_uc=compute_daily_uc,
            user_id=current_user.id,
            dates={result.date},
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
