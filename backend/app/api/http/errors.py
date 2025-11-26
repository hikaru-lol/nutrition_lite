
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.domain.auth import errors as auth_errors
from app.application.target import errors as target_app_errors
from app.domain.target import errors as target_domain_errors
from app.domain.profile import errors as profile_domain_errors
from app.domain.meal import errors as meal_domain_errors
from app.domain.nutrition import errors as nutrition_domain_errors
from app.domain.meal.errors import InvalidMealTypeError, InvalidMealIndexError
import logging

logger = logging.getLogger(__name__)


def error_response(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
            }
        },
    )


async def auth_error_handler(request: Request, exc: auth_errors.AuthError):
    # 監査用ログ（warning レベル）
    logger.warning(
        "AuthError: type=%s path=%s client=%s msg=%s",
        exc.__class__.__name__,
        request.url.path,
        request.client.host if request.client else None,
        str(exc),
    )

    if isinstance(exc, auth_errors.EmailAlreadyUsedError):
        return error_response(
            "EMAIL_ALREADY_IN_USE",
            "このメールアドレスは既に登録されています。",
            status.HTTP_409_CONFLICT,
        )
    if isinstance(exc, auth_errors.InvalidCredentialsError):
        return error_response(
            "INVALID_CREDENTIALS",
            "メールアドレスまたはパスワードが正しくありません。",
            status.HTTP_401_UNAUTHORIZED,
        )
    if isinstance(exc, auth_errors.InvalidRefreshTokenError):
        return error_response(
            "UNAUTHORIZED",
            "リフレッシュトークンが無効または期限切れです。",
            status.HTTP_401_UNAUTHORIZED,
        )
    if isinstance(exc, auth_errors.UserNotFoundError):
        return error_response(
            "USER_NOT_FOUND",
            "ユーザーが見つかりません。",
            status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, auth_errors.InvalidEmailFormatError):
        return error_response(
            "INVALID_EMAIL_FORMAT",
            "メールアドレスの形式が正しくありません。",
            status.HTTP_400_BAD_REQUEST,
        )

    # 想定外の AuthError（基本ないはずだが念のため）
    logger.exception("Unhandled AuthError: %s", exc)
    return error_response(
        "INTERNAL_ERROR",
        "予期しないエラーが発生しました。",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# 🔽 これを追加（リクエストのバリデーションエラー → 400）
async def validation_error_handler(_: Request, exc: RequestValidationError):
    # ここで exc.errors() を message に入れても OK（詳細が欲しくなったら拡張）
    return error_response(
        "VALIDATION_ERROR",
        "リクエストの形式が正しくありません。",
        status.HTTP_400_BAD_REQUEST,
    )


async def target_error_handler(request: Request, exc: target_app_errors.TargetError):
    logger.warning(
        "TargetError: type=%s path=%s client=%s msg=%s",
        exc.__class__.__name__,
        request.url.path,
        request.client.host if request.client else None,
        str(exc),
    )

    if isinstance(exc, target_app_errors.TargetNotFoundError):
        return error_response(
            "TARGET_NOT_FOUND",
            "ターゲットが見つかりません。",
            status.HTTP_404_NOT_FOUND,
        )

    # LLM によるターゲット生成失敗
    if isinstance(exc, target_app_errors.TargetGenerationFailedError):
        return error_response(
            "TARGET_GENERATION_FAILED",
            "栄養ターゲットの自動生成に失敗しました。",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # 上限超えをドメイン側で投げている場合（必要であれば）
    if isinstance(exc, target_app_errors.TargetLimitExceededError):
        return error_response(
            "TARGET_LIMIT_EXCEEDED",
            "作成できるターゲットの上限数に達しています。",
            status.HTTP_409_CONFLICT,
        )

    # プロフィールが見つからない場合
    if isinstance(exc, profile_domain_errors.ProfileNotFoundError):
        return error_response(
            "PROFILE_NOT_FOUND",
            "プロフィールが見つかりません。",
            status.HTTP_404_NOT_FOUND,
        )

    logger.exception("Unhandled TargetError: %s", exc)
    return error_response(
        "INTERNAL_ERROR",
        "予期しないエラーが発生しました。",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def target_domain_error_handler(
    request: Request,
    exc: target_domain_errors.TargetDomainError,
):
    logger.warning(
        "TargetDomainError: type=%s path=%s client=%s msg=%s",
        exc.__class__.__name__,
        request.url.path,
        request.client.host if request.client else None,
        str(exc),
    )

    if isinstance(exc, target_domain_errors.InvalidTargetNutrientError):
        return error_response(
            "INVALID_TARGET_NUTRIENT",
            "指定された栄養素コードが不正です。",
            status.HTTP_400_BAD_REQUEST,
        )

    logger.exception("Unhandled TargetDomainError: %s", exc)
    return error_response(
        "INTERNAL_ERROR",
        "予期しないエラーが発生しました。",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def meal_domain_error_handler(
    request: Request,
    exc: meal_domain_errors.MealDomainError,
) -> JSONResponse:
    """
    Meal ドメインのエラーを HTTP レスポンスに変換するハンドラ。
    """
    logger.warning(
        "MealDomainError: type=%s path=%s client=%s msg=%s",
        exc.__class__.__name__,
        request.url.path,
        request.client.host if request.client else None,
        str(exc),
    )

    # 400 系
    if isinstance(exc, meal_domain_errors.InvalidMealTypeError):
        return error_response(
            status_code=400,
            code="INVALID_MEAL_TYPE",
            message=str(exc) or "Invalid meal_type",
        )

    if isinstance(exc, meal_domain_errors.InvalidMealIndexError):
        return error_response(
            status_code=400,
            code="INVALID_MEAL_INDEX",
            message=str(exc) or "Invalid meal_index for given meal_type",
        )

    if isinstance(exc, meal_domain_errors.InvalidFoodAmountError):
        return error_response(
            status_code=400,
            code="INVALID_FOOD_AMOUNT",
            message=str(exc) or "Invalid food amount",
        )

    # 404 系
    if isinstance(exc, meal_domain_errors.FoodEntryNotFoundError):
        return error_response(
            status_code=404,
            code="FOOD_ENTRY_NOT_FOUND",
            message=str(exc) or "FoodEntry not found",
        )

    # 想定外の MealDomainError（念のため）→ 500 扱い
    logger.exception("Unhandled MealDomainError: %s", exc)
    return error_response(
        "INTERNAL_ERROR",
        "予期しないエラーが発生しました。",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def nutrition_domain_error_handler(
    request: Request,
    exc: nutrition_domain_errors.NutritionDomainError,
) -> JSONResponse:
    if isinstance(exc, nutrition_domain_errors.NutritionEstimationFailedError):
        return error_response(
            status_code=500,
            code="NUTRITION_ESTIMATION_FAILED",
            message=str(exc) or "Failed to estimate nutrition",
        )
    # 万が一 NutritionDomainError の別バリエーションが増えても、ここで 500 にフォールバック
    return error_response(
        status_code=500,
        code="NUTRITION_ERROR",
        message=str(exc) or "Nutrition domain error",
    )


async def meal_slot_error_handler(
    request: Request,
    exc,
) -> JSONResponse:
    # meal_type / meal_index のバリデーションエラー用
    if isinstance(exc, InvalidMealTypeError):
        return error_response(
            status_code=400,
            code="INVALID_MEAL_TYPE",
            message=str(exc) or "Invalid meal_type",
        )
    if isinstance(exc, InvalidMealIndexError):
        return error_response(
            status_code=400,
            code="INVALID_MEAL_INDEX",
            message=str(exc) or "Invalid meal_index for given meal_type",
        )

    # ここまで来ることはあまりない想定だが念のため
    return error_response(
        status_code=400,
        code="INVALID_MEAL_SLOT",
        message=str(exc) or "Invalid meal slot",
    )
