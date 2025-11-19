from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError

from app.application.auth.ports.token_service_port import (
    TokenServicePort,
    TokenPayload,
    TokenPair,
)
from app.domain.auth.value_objects import UserPlan
from app.domain.auth.errors import InvalidRefreshTokenError, InvalidCredentialsError
from app.settings import settings


class JwtTokenService(TokenServicePort):
    """
    JWT ベースの TokenServicePort 実装。

    - HS256 + シークレットキー
    - access / refresh で TTL を分ける
    """

    def __init__(
        self,
        secret_key: str | None = None,
        algorithm: str | None = None,
        access_ttl_minutes: int | None = None,
        refresh_ttl_days: int | None = None,
    ) -> None:
        self._secret_key = secret_key or settings.JWT_SECRET_KEY
        self._algorithm = algorithm or settings.JWT_ALGORITHM
        self._access_ttl = timedelta(
            minutes=access_ttl_minutes or settings.ACCESS_TOKEN_TTL_MINUTES
        )
        self._refresh_ttl = timedelta(
            days=refresh_ttl_days or settings.REFRESH_TOKEN_TTL_DAYS
        )

    # ------------------------------------------------------------------
    # ヘルパー
    # ------------------------------------------------------------------

    def _encode(self, payload: dict, expires_in: timedelta) -> tuple[str, datetime]:
        now = datetime.now(timezone.utc)
        exp = now + expires_in
        to_encode = {**payload, "exp": exp}
        token = jwt.encode(to_encode, self._secret_key,
                           algorithm=self._algorithm)
        return token, exp

    def _decode(self, token: str) -> dict:
        return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])

    # ------------------------------------------------------------------
    # Port 実装
    # ------------------------------------------------------------------

    def issue_tokens(self, payload: TokenPayload) -> TokenPair:
        base_payload = {
            "sub": payload.user_id,
            "plan": getattr(payload.plan, "value", str(payload.plan)),
        }

        access_token, access_exp = self._encode(base_payload, self._access_ttl)
        refresh_token, refresh_exp = self._encode(
            base_payload, self._refresh_ttl)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_at=access_exp,
            refresh_expires_at=refresh_exp,
        )

    def _payload_from_claims(self, claims: dict) -> TokenPayload:
        user_id = str(claims.get("sub"))
        plan_raw = claims.get("plan")
        try:
            plan = UserPlan(plan_raw)
        except Exception:
            plan = plan_raw  # 何かおかしくてもとりあえずそのまま
        return TokenPayload(user_id=user_id, plan=plan)

    def verify_access_token(self, token: str) -> TokenPayload:
        try:
            claims = self._decode(token)
        except JWTError as e:
            # access token の場合は「認証エラー」として扱う
            raise InvalidCredentialsError(
                "Invalid or expired access token") from e
        return self._payload_from_claims(claims)

    def verify_refresh_token(self, token: str) -> TokenPayload:
        try:
            claims = self._decode(token)
        except JWTError as e:
            # refresh token は InvalidRefreshTokenError を使う
            raise InvalidRefreshTokenError(
                "Invalid or expired refresh token") from e
        return self._payload_from_claims(claims)
