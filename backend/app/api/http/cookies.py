# app/api/http/cookies.py

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Response

from app.application.auth.ports.token_service_port import TokenPair

ACCESS_COOKIE_NAME = "ACCESS_TOKEN"
REFRESH_COOKIE_NAME = "REFRESH_TOKEN"


def _max_age_from_expires_at(expires_at: datetime) -> int:
    """
    TokenPair の access_expires_at / refresh_expires_at から max_age 秒を計算する。
    マイナスにならないように 0 でクリップ。
    """
    now = datetime.now(timezone.utc)
    seconds = int((expires_at - now).total_seconds())
    return max(seconds, 0)


def set_auth_cookies(response: Response, tokens: TokenPair) -> None:
    """
    認証用の ACCESS_TOKEN / REFRESH_TOKEN クッキーをレスポンスにセットする。
    """
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=tokens.access_token,
        httponly=True,
        secure=False,        # ★ テスト・ローカルでは False、本番では True 推奨
        samesite="lax",
        path="/",
        max_age=_max_age_from_expires_at(tokens.access_expires_at),
    )
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=tokens.refresh_token,
        httponly=True,
        secure=False,        # ★ 同上
        samesite="lax",
        path="/",
        max_age=_max_age_from_expires_at(tokens.refresh_expires_at),
    )


def clear_auth_cookies(response: Response) -> None:
    """
    認証用クッキーを削除する。
    """
    response.delete_cookie(key=ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/")
