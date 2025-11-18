from fastapi import Response

from app.application.auth.dto import TokenPairDTO  # こんな DTO がある前提

ACCESS_COOKIE_NAME = "ACCESS_TOKEN"
REFRESH_COOKIE_NAME = "REFRESH_TOKEN"


def set_auth_cookies(response: Response, tokens: TokenPairDTO) -> None:
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=tokens.access_token,
        httponly=True,
        secure=True,          # dev なら False にしてもよい
        samesite="lax",
        path="/",
        max_age=tokens.access_expires_in,
    )
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
        max_age=tokens.refresh_expires_in,
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(key=ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/")
