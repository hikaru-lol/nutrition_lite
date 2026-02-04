from __future__ import annotations

from datetime import date as DateType
from logging import getLogger

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.http.dependencies.auth import get_current_user_dto
from app.api.http.schemas.meal_recommendation import (
    GenerateMealRecommendationRequest,
    GenerateMealRecommendationResponse,
    GetMealRecommendationResponse,
    ListMealRecommendationsResponse,
    MealRecommendationResponse,
    RecommendedMealResponse,
)
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.nutrition.ports.uow_port import NutritionUnitOfWorkPort
from app.application.nutrition.use_cases.generate_meal_recommendation import (
    GenerateMealRecommendationInput,
    GenerateMealRecommendationUseCase,
)
from app.application.nutrition.use_cases.list_meal_recommendations import (
    ListMealRecommendationsInput,
    ListMealRecommendationsUseCase,
)
from app.di.container import (
    get_generate_meal_recommendation_use_case,
    get_list_meal_recommendations_use_case,
    get_nutrition_uow,
)
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.meal_recommendation import MealRecommendation
from app.domain.nutrition.errors import (
    NotEnoughDailyReportsError,
    MealRecommendationCooldownError,
    MealRecommendationDailyLimitError,
)
from app.domain.meal.errors import DailyLogProfileNotFoundError

logger = getLogger(__name__)

router = APIRouter(prefix="/meal-recommendations",
                   tags=["Meal Recommendations"])


def _to_response(recommendation: MealRecommendation) -> MealRecommendationResponse:
    """ドメインエンティティ -> レスポンススキーマ変換"""
    # RecommendedMeal エンティティ -> レスポンススキーマ変換
    recommended_meals_response = [
        RecommendedMealResponse(
            title=meal.title,
            description=meal.description,
            ingredients=meal.ingredients,
            nutrition_focus=meal.nutrition_focus,
        )
        for meal in recommendation.recommended_meals
    ]

    return MealRecommendationResponse(
        id=recommendation.id.value,
        user_id=recommendation.user_id.value,
        generated_for_date=recommendation.generated_for_date,
        body=recommendation.body,
        tips=recommendation.tips,
        recommended_meals=recommended_meals_response,
        created_at=recommendation.created_at,
    )


@router.post(
    "/generate",
    response_model=GenerateMealRecommendationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Not enough daily reports"},
        401: {"description": "Unauthorized"},
        403: {"description": "Premium feature required"},
        404: {"description": "Profile not found"},
        429: {"description": "Rate limit exceeded (cooldown or daily limit)"},
        500: {"description": "Failed to generate recommendation"},
    },
)
def generate_meal_recommendation(
    request: GenerateMealRecommendationRequest,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: GenerateMealRecommendationUseCase = Depends(
        get_generate_meal_recommendation_use_case
    ),
) -> GenerateMealRecommendationResponse:
    """
    食事提案を生成する (プレミアム機能)。

    直近1-5日分の栄養レポートを基にOpenAIで次の食事を提案。
    """
    user_id = UserId(current_user.id)

    input_dto = GenerateMealRecommendationInput(
        user_id=user_id,
        base_date=request.date,
    )

    try:
        recommendation = use_case.execute(input_dto)
        return GenerateMealRecommendationResponse(
            recommendation=_to_response(recommendation)
        )
    except NotEnoughDailyReportsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough daily reports. {str(e)}"
        ) from e
    except DailyLogProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete your profile first."
        ) from e
    except MealRecommendationCooldownError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Please wait {e.remaining_minutes} minutes before generating again."
        ) from e
    except MealRecommendationDailyLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily limit reached: {e.current_count}/{e.limit} recommendations per day."
        ) from e
    except Exception as e:
        logger.exception("Failed to generate meal recommendation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendation"
        ) from e


@router.get(
    "/{date}",
    response_model=GetMealRecommendationResponse,
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "Recommendation not found"},
    },
)
def get_meal_recommendation(
    date: DateType,
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    nutrition_uow: NutritionUnitOfWorkPort = Depends(get_nutrition_uow),
) -> GetMealRecommendationResponse:
    """
    特定日の食事提案を取得する。
    """
    user_id = UserId(current_user.id)

    with nutrition_uow as uow:
        recommendation = uow.meal_recommendation_repo.get_by_user_and_date(
            user_id=user_id,
            generated_for_date=date,
        )

        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation not found for date: {date}"
            )

        return GetMealRecommendationResponse(
            recommendation=_to_response(recommendation)
        )


@router.get(
    "",
    response_model=ListMealRecommendationsResponse,
    responses={
        401: {"description": "Unauthorized"},
    },
)
def list_meal_recommendations(
    limit: int = Query(default=10, ge=1, le=50, description="取得件数"),
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: ListMealRecommendationsUseCase = Depends(get_list_meal_recommendations_use_case),
) -> ListMealRecommendationsResponse:
    """
    食事提案の一覧を取得する（作成日時の新しい順）。
    """
    user_id = UserId(current_user.id)

    input_dto = ListMealRecommendationsInput(
        user_id=user_id,
        limit=limit,
    )

    recommendations = use_case.execute(input_dto)

    return ListMealRecommendationsResponse(
        recommendations=[_to_response(rec) for rec in recommendations]
    )
