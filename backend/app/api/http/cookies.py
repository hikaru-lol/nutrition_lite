from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Response

from app.application.auth.ports.token_service_port import TokenPair
from app.settings import settings

ACCESS_COOKIE_NAME = "ACCESS_TOKEN"
REFRESH_COOKIE_NAME = "REFRESH_TOKEN"


def _max_age_from_expires_at(expires_at: datetime) -> int:
    """
    TokenPair の expires_at から max_age 秒を計算。
    マイナスにならないように 0 でクリップ。
    """
    now = datetime.now(timezone.utc)
    return max(int((expires_at - now).total_seconds()), 0)


def set_auth_cookies(response: Response, tokens: TokenPair) -> None:
    """
    認証用の ACCESS_TOKEN / REFRESH_TOKEN クッキーをレスポンスにセットする。
    - HttpOnly
    - path="/"
    - secure / samesite は settings から制御
    """
    cookie_common = {
        "httponly": True,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
        "path": "/",
        # 必要になったら domain もここで集中管理:
        # "domain": settings.BACKEND_DOMAIN,
    }

    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=tokens.access_token,
        max_age=_max_age_from_expires_at(tokens.access_expires_at),
        **cookie_common,
    )
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=tokens.refresh_token,
        max_age=_max_age_from_expires_at(tokens.refresh_expires_at),
        **cookie_common,
    )


def clear_auth_cookies(response: Response) -> None:
    """
    認証用クッキーを削除する。
    """
    response.delete_cookie(key=ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/")
