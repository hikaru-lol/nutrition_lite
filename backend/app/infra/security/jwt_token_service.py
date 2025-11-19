from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError

from app.application.auth.ports.token_service_port import (
    TokenServicePort,
    TokenPayload,
    TokenPair,
)
from app.domain.auth.value_objects import UserPlan
from app.domain.auth.errors import InvalidCredentialsError
from app.settings import settings


class JwtTokenService(TokenServicePort):
    """
    JWT ベースの TokenServicePort 実装。

    - HS256 + シークレットキー（設定ファイルから取得）
    - Access / Refresh で TTL を分けて管理
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
    # 内部ヘルパー
    # ------------------------------------------------------------------

    def _encode(self, payload: dict, ttl: timedelta) -> tuple[str, datetime]:
        now = datetime.now(timezone.utc)
        exp = now + ttl
        to_encode = {**payload, "exp": exp}
        token = jwt.encode(to_encode, self._secret_key,
                           algorithm=self._algorithm)
        return token, exp

    def _decode(self, token: str) -> dict:
        return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])

    def _payload_from_claims(self, claims: dict) -> TokenPayload:
        user_id = str(claims.get("sub"))
        plan_raw = claims.get("plan")
        try:
            plan = UserPlan(plan_raw)
        except Exception:
            # enum じゃなかったときも一応動くように
            plan = plan_raw  # type: ignore[assignment]
        return TokenPayload(user_id=user_id, plan=plan)

    # ------------------------------------------------------------------
    # Port 実装
    # ------------------------------------------------------------------

    def issue_tokens(self, payload: TokenPayload) -> TokenPair:
        """
        Access / Refresh の 2 種類のトークンを発行し、
        それぞれの expires_at を持つ TokenPair を返す。
        """
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

    def verify_access_token(self, token: str) -> TokenPayload:
        """
        Access Token の検証。
        無効 / 期限切れの場合は InvalidCredentialsError を投げる。
        （/auth/me などで直接ドメインエラーとして扱いたいのでここで包む）
        """
        try:
            claims = self._decode(token)
        except JWTError as e:
            raise InvalidCredentialsError(
                "Invalid or expired access token") from e
        return self._payload_from_claims(claims)

    def verify_refresh_token(self, token: str) -> TokenPayload:
        """
        Refresh Token の検証。
        無効 / 期限切れの場合は JWTError を投げるが、
        呼び出し側（RefreshTokenUseCase）で InvalidRefreshTokenError にまとめているので、
        ここではあえてドメインエラーに包まない。
        """
        claims = self._decode(token)  # JWTError はそのまま投げる
        return self._payload_from_claims(claims)
