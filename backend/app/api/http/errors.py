# app/api/http/errors.py

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.domain.auth import errors as auth_errors


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


async def auth_error_handler(_: Request, exc: auth_errors.AuthError):
    if isinstance(exc, auth_errors.EmailAlreadyUsedError):
        return error_response("EMAIL_ALREADY_IN_USE", "このメールアドレスは既に登録されています。", status.HTTP_409_CONFLICT)
    if isinstance(exc, auth_errors.InvalidCredentialsError):
        return error_response("INVALID_CREDENTIALS", "メールアドレスまたはパスワードが正しくありません。", status.HTTP_401_UNAUTHORIZED)
    if isinstance(exc, auth_errors.InvalidRefreshTokenError):
        return error_response("UNAUTHORIZED", "リフレッシュトークンが無効または期限切れです。", status.HTTP_401_UNAUTHORIZED)
    if isinstance(exc, auth_errors.UserNotFoundError):
        return error_response("USER_NOT_FOUND", "ユーザーが見つかりません。", status.HTTP_401_UNAUTHORIZED)

    # fallback
    return error_response("INTERNAL_ERROR", "予期しないエラーが発生しました。", status.HTTP_500_INTERNAL_SERVER_ERROR)
