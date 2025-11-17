from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError

from app.application.auth.ports.token_service_port import (
    TokenServicePort,
    TokenPayload,
    TokenPair,
)
from app.domain.auth.value_objects import UserPlan


class InvalidTokenError(Exception):
    pass


class JwtTokenService(TokenServicePort):
    def __init__(
        self,
        secret_key: str | None = None,
        algorithm: str | None = None,
        access_token_ttl_minutes: int | None = None,
        refresh_token_ttl_days: int | None = None,
    ) -> None:
        self._secret_key = secret_key or os.getenv(
            "JWT_SECRET", "dev-secret-change-me")
        self._algorithm = algorithm or os.getenv("JWT_ALGORITHM", "HS256")
        self._access_token_ttl_minutes = access_token_ttl_minutes or int(
            os.getenv("ACCESS_TOKEN_TTL_MINUTES", "15")
        )
        self._refresh_token_ttl_days = refresh_token_ttl_days or int(
            os.getenv("REFRESH_TOKEN_TTL_DAYS", "7")
        )

    def _now(self) -> datetime:
        # UTC timezone-aware にしておく
        return datetime.now(timezone.utc)

    def issue_tokens(self, payload: TokenPayload) -> TokenPair:
        now = self._now()
        access_exp = now + timedelta(minutes=self._access_token_ttl_minutes)
        refresh_exp = now + timedelta(days=self._refresh_token_ttl_days)

        base_claims = {
            "sub": payload.user_id,
            "plan": payload.plan.value,
            "iat": int(now.timestamp()),
        }

        access_claims = {
            **base_claims,
            "type": "access",
            "exp": int(access_exp.timestamp()),
        }

        refresh_claims = {
            **base_claims,
            "type": "refresh",
            "exp": int(refresh_exp.timestamp()),
        }

        access_token = jwt.encode(
            access_claims, self._secret_key, algorithm=self._algorithm)
        refresh_token = jwt.encode(
            refresh_claims, self._secret_key, algorithm=self._algorithm)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_at=access_exp,
            refresh_expires_at=refresh_exp,
        )

    def _decode_and_validate(self, token: str, expected_type: str) -> TokenPayload:
        try:
            claims = jwt.decode(token, self._secret_key,
                                algorithms=[self._algorithm])
        except JWTError as e:
            raise InvalidTokenError("Invalid token") from e

        token_type = claims.get("type")
        if token_type != expected_type:
            raise InvalidTokenError("Invalid token type")

        user_id = claims.get("sub")
        plan_str = claims.get("plan")
        if not user_id or not plan_str:
            raise InvalidTokenError("Invalid token payload")

        try:
            plan = UserPlan(plan_str)
        except ValueError as e:
            raise InvalidTokenError("Invalid plan in token") from e

        return TokenPayload(user_id=user_id, plan=plan)

    def verify_access_token(self, token: str) -> TokenPayload:
        return self._decode_and_validate(token, expected_type="access")

    def verify_refresh_token(self, token: str) -> TokenPayload:
        return self._decode_and_validate(token, expected_type="refresh")
