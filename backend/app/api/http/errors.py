
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.domain.auth import errors as auth_errors

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
    # 簡易的な監査ログ
    logger.warning(
        "AuthError: type=%s path=%s code_maybe=%s msg=%s",
        exc.__class__.__name__,
        request.url.path,
        getattr(exc, "code", None),
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

    logger.exception("Unhandled AuthError: %s", exc)
    # fallback
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
