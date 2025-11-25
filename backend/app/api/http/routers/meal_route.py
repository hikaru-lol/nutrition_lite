from __future__ import annotations

from datetime import date as DateType

from fastapi import APIRouter, Depends, Query, Path, Response, status

from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.meal.dto.food_entry_dto import FoodEntryDTO
from app.application.meal.use_cases.create_food_entry import CreateFoodEntryUseCase
from app.application.meal.use_cases.update_food_entry import UpdateFoodEntryUseCase
from app.application.meal.use_cases.delete_food_entry import DeleteFoodEntryUseCase
from app.application.meal.use_cases.list_food_entries_by_date import ListFoodEntriesByDateUseCase
from app.api.http.schemas.meal import (
    MealItemRequest,
    MealItemResponse,
    MealItemListResponse,
)
from app.application.meal.dto.food_entry_dto import (
    FoodEntryDTO,
    CreateFoodEntryInputDTO,
    UpdateFoodEntryInputDTO,
)
from app.api.http.dependencies.auth import get_current_user_dto

from app.di.container import (
    get_create_food_entry_use_case,
    get_update_food_entry_use_case,
    get_delete_food_entry_use_case,
    get_list_food_entries_by_date_use_case,
)

router = APIRouter(tags=["Meal"])


# --- Helpers -----------------------------------------------------------


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


# --- Routes ------------------------------------------------------------


@router.post(
    "/meal-items",
    response_model=MealItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_meal_item(
    body: MealItemRequest,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: CreateFoodEntryUseCase = Depends(get_create_food_entry_use_case),
) -> MealItemResponse:
    """
    FoodEntry（1品の食事ログ）を新規作成する。
    """

    input_dto = CreateFoodEntryInputDTO(
        date=body.date,
        meal_type=body.meal_type.value,  # Enum -> str ("main" / "snack")
        meal_index=body.meal_index,
        name=body.name,
        amount_value=body.amount_value,
        amount_unit=body.amount_unit,
        serving_count=body.serving_count,
        note=body.note,
    )

    dto = use_case.execute(current_user.id, input_dto)
    return _dto_to_response(dto)


@router.get(
    "/meal-items",
    response_model=MealItemListResponse,
)
def list_meal_items_by_date(
    date: DateType = Query(..., description="対象日 (YYYY-MM-DD)"),
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: ListFoodEntriesByDateUseCase = Depends(
        get_list_food_entries_by_date_use_case),
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
)
def update_meal_item(
    entry_id: str = Path(..., description="FoodEntry ID (UUID 文字列)"),
    body: MealItemRequest = ...,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: UpdateFoodEntryUseCase = Depends(get_update_food_entry_use_case),
) -> MealItemResponse:
    """
    既存の FoodEntry を更新する。（現時点ではフル更新）
    """

    input_dto = UpdateFoodEntryInputDTO(
        entry_id=entry_id,
        date=body.date,
        meal_type=body.meal_type.value,
        meal_index=body.meal_index,
        name=body.name,
        amount_value=body.amount_value,
        amount_unit=body.amount_unit,
        serving_count=body.serving_count,
        note=body.note,
    )

    dto = use_case.execute(current_user.id, input_dto)
    return _dto_to_response(dto)


@router.delete(
    "/meal-items/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_meal_item(
    entry_id: str = Path(..., description="FoodEntry ID (UUID 文字列)"),
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: DeleteFoodEntryUseCase = Depends(get_delete_food_entry_use_case),
) -> Response:
    """
    FoodEntry を削除する。

    - Repository 実装側ではソフトデリートを想定。
    - 既に削除済みの場合でも 204 を返すことで冪等性を担保。
    """

    use_case.execute(current_user.id, entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
