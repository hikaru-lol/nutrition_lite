from __future__ import annotations

import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.application.target import errors as target_app_errors
from app.domain.auth import errors as auth_errors
from app.domain.meal import errors as meal_domain_errors
from app.domain.meal.errors import InvalidMealIndexError, InvalidMealTypeError, DailyLogProfileNotFoundError
from app.domain.nutrition import errors as nutrition_domain_errors
from app.domain.target import errors as target_domain_errors

logger = logging.getLogger(__name__)


# === 共通ユーティリティ =====================================================


def error_response(*, code: str, message: str, status_code: int) -> JSONResponse:
    """
    エラーレスポンスを統一フォーマットで返すためのヘルパー。
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
            }
        },
    )


# === Auth ===================================================================


async def auth_error_handler(request: Request, exc: auth_errors.AuthError) -> JSONResponse:
    """
    認証 / 認可まわりのドメインエラーを HTTP レスポンスにマッピングするハンドラ。
    """
    logger.warning(
        "AuthError: type=%s path=%s client=%s msg=%s",
        exc.__class__.__name__,
        request.url.path,
        request.client.host if request.client else None,
        str(exc),
    )

    if isinstance(exc, auth_errors.EmailAlreadyUsedError):
        return error_response(
            code="EMAIL_ALREADY_IN_USE",
            message="このメールアドレスは既に登録されています。",
            status_code=status.HTTP_409_CONFLICT,
        )

    if isinstance(exc, auth_errors.InvalidAccessTokenError):
        return error_response(
            code="INVALID_ACCESS_TOKEN",
            message="アクセストークンが無効または期限切れです。",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, auth_errors.InvalidCredentialsError):
        return error_response(
            code="INVALID_CREDENTIALS",
            message="メールアドレスまたはパスワードが正しくありません。",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, auth_errors.InvalidRefreshTokenError):
        return error_response(
            code="UNAUTHORIZED",
            message="リフレッシュトークンが無効または期限切れです。",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, auth_errors.UserNotFoundError):
        return error_response(
            code="USER_NOT_FOUND",
            message="ユーザーが見つかりません。",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, auth_errors.InvalidEmailFormatError):
        return error_response(
            code="INVALID_EMAIL_FORMAT",
            message="メールアドレスの形式が正しくありません。",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # 想定外の AuthError（基本ないはずだが念のため）
    logger.exception("Unhandled AuthError: %s", exc)
    return error_response(
        code="INTERNAL_ERROR",
        message="予期しないエラーが発生しました。",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# === Validation =============================================================


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """
    FastAPI / Pydantic のリクエストバリデーションエラーを 400 にマッピングするハンドラ。
    """
    logger.warning("RequestValidationError: %s", exc)
    # 必要に応じて exc.errors() を message に含めてもよい
    return error_response(
        code="VALIDATION_ERROR",
        message="リクエストの形式が正しくありません。",
        status_code=status.HTTP_400_BAD_REQUEST,
    )


# === Target (Application エラー) ===========================================


async def target_error_handler(
    request: Request,
    exc: target_app_errors.TargetError,
) -> JSONResponse:
    """
    Target アプリケーション層のエラーを HTTP レスポンスにマッピングするハンドラ。
    """
    logger.warning(
        "TargetError: type=%s path=%s client=%s msg=%s",
        exc.__class__.__name__,
        request.url.path,
        request.client.host if request.client else None,
        str(exc),
    )

    if isinstance(exc, target_app_errors.TargetNotFoundError):
        return error_response(
            code="TARGET_NOT_FOUND",
            message="ターゲットが見つかりません。",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, target_app_errors.TargetGenerationFailedError):
        return error_response(
            code="TARGET_GENERATION_FAILED",
            message="栄養ターゲットの自動生成に失敗しました。",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, target_app_errors.TargetLimitExceededError):
        return error_response(
            code="TARGET_LIMIT_EXCEEDED",
            message="作成できるターゲットの上限数に達しています。",
            status_code=status.HTTP_409_CONFLICT,
        )

    if isinstance(exc, target_app_errors.TargetProfileNotFoundError):
        return error_response(
            code="TARGET_PROFILE_NOT_FOUND",
            message="ターゲットを生成するためのプロフィールが見つかりません。",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    logger.exception("Unhandled TargetError: %s", exc)
    return error_response(
        code="INTERNAL_ERROR",
        message="予期しないエラーが発生しました。",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# === Target (Domain エラー) ================================================


async def target_domain_error_handler(
    request: Request,
    exc: target_domain_errors.TargetDomainError,
) -> JSONResponse:
    """
    Target ドメイン層のエラーを HTTP レスポンスにマッピングするハンドラ。
    """
    logger.warning(
        "TargetDomainError: type=%s path=%s client=%s msg=%s",
        exc.__class__.__name__,
        request.url.path,
        request.client.host if request.client else None,
        str(exc),
    )

    if isinstance(exc, target_domain_errors.InvalidTargetNutrientError):
        return error_response(
            code="INVALID_TARGET_NUTRIENT",
            message="指定された栄養素コードが不正です。",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    logger.exception("Unhandled TargetDomainError: %s", exc)
    return error_response(
        code="INTERNAL_ERROR",
        message="予期しないエラーが発生しました。",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# === Meal (Domain エラー) ==================================================


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
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_MEAL_TYPE",
            message=str(exc) or "Invalid meal_type",
        )

    if isinstance(exc, meal_domain_errors.InvalidMealIndexError):
        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_MEAL_INDEX",
            message=str(exc) or "Invalid meal_index for given meal_type",
        )

    if isinstance(exc, meal_domain_errors.InvalidFoodAmountError):
        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_FOOD_AMOUNT",
            message=str(exc) or "Invalid food amount",
        )

    if isinstance(exc, DailyLogProfileNotFoundError):
        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="DAILY_LOG_PROFILE_NOT_FOUND",
            message="日次ログの判定にはプロフィールの設定が必要です。",
        )

    if isinstance(exc, meal_domain_errors.InvalidMealsPerDayError):
        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_MEALS_PER_DAY",
            message="Invalid meals_per_day",
        )

    # 404 系
    if isinstance(exc, meal_domain_errors.FoodEntryNotFoundError):
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code="FOOD_ENTRY_NOT_FOUND",
            message=str(exc) or "FoodEntry not found",
        )

    # 想定外の MealDomainError → 500 扱い
    logger.exception("Unhandled MealDomainError: %s", exc)
    return error_response(
        code="INTERNAL_ERROR",
        message="予期しないエラーが発生しました。",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# === Nutrition (Domain エラー) =============================================


async def nutrition_domain_error_handler(
    request: Request,
    exc: nutrition_domain_errors.NutritionDomainError,
) -> JSONResponse:
    """
    Nutrition ドメインのエラーを HTTP レスポンスに変換するハンドラ。
    """
    logger.warning(
        "NutritionDomainError: type=%s path=%s client=%s msg=%s",
        exc.__class__.__name__,
        request.url.path,
        request.client.host if request.client else None,
        str(exc),
    )

    # LLM などによる栄養推定失敗
    if isinstance(exc, nutrition_domain_errors.NutritionEstimationFailedError):
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="NUTRITION_ESTIMATION_FAILED",
            message=str(exc) or "Failed to estimate nutrition",
        )

    # 日次ログが「記録完了」になっていない場合
    if isinstance(exc, nutrition_domain_errors.DailyLogNotCompletedError):
        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="DAILY_LOG_NOT_COMPLETED",
            message="指定された日付の食事ログがまだ記録完了になっていません。",
        )

    # すでにその日のレポートが存在する場合
    if isinstance(exc, nutrition_domain_errors.DailyNutritionReportAlreadyExistsError):
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            code="DAILY_NUTRITION_REPORT_ALREADY_EXISTS",
            message="指定された日付の栄養レポートは既に存在します。",
        )

    # 万が一 NutritionDomainError の別バリエーションが増えても、ここで 500 にフォールバック
    logger.exception("Unhandled NutritionDomainError: %s", exc)
    return error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="NUTRITION_ERROR",
        message=str(exc) or "Nutrition domain error",
    )


# === Meal slot (変換 / バリデーション系) ===================================


async def meal_slot_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    meal_type / meal_index のスロット指定に関するエラーをまとめて扱うハンドラ。
    """
    logger.warning(
        "MealSlotError: type=%s path=%s client=%s msg=%s",
        exc.__class__.__name__,
        request.url.path,
        request.client.host if request.client else None,
        str(exc),
    )

    if isinstance(exc, InvalidMealTypeError):
        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_MEAL_TYPE",
            message=str(exc) or "Invalid meal_type",
        )

    if isinstance(exc, InvalidMealIndexError):
        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_MEAL_INDEX",
            message=str(exc) or "Invalid meal_index for given meal_type",
        )

    # ここまで来ることはあまりない想定だが念のため
    return error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        code="INVALID_MEAL_SLOT",
        message=str(exc) or "Invalid meal slot",
    )
