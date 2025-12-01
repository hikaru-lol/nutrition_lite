from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.application.auth.ports.token_service_port import (
    TokenPayload,
    TokenPair,
    TokenServicePort,
)
from app.domain.auth.errors import InvalidCredentialsError
from app.domain.auth.value_objects import UserPlan
from app.settings import settings


class JwtTokenService(TokenServicePort):
    """
    JWT ベースの TokenServicePort 実装。

    - HS256 + シークレットキー（settings から取得）
    - Access / Refresh で有効期限 (TTL) を分けて管理
    """

    # ------------------------------------------------------------------
    # コンストラクタ
    # ------------------------------------------------------------------

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
        """
        任意の payload に有効期限 (exp) を付与して JWT を生成する。
        """
        now = datetime.now(timezone.utc)
        exp = now + ttl
        to_encode = {**payload, "exp": exp}
        token = jwt.encode(to_encode, self._secret_key,
                           algorithm=self._algorithm)
        return token, exp

    def _decode(self, token: str) -> dict:
        """
        JWT を検証・デコードして claims を返す。

        Raises:
            JWTError: 署名不正 / 期限切れ など JWT レベルのエラー
        """
        return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])

    def _payload_from_claims(self, claims: dict) -> TokenPayload:
        """
        JWT の claims からアプリケーションで使う TokenPayload へ変換する。
        """
        # sub: subject = user_id
        user_id = str(claims.get("sub"))

        # plan は Enum(UserPlan) 前提だが、念のため文字列なども許容
        plan_raw = claims.get("plan")
        try:
            plan = UserPlan(plan_raw)
        except Exception:
            # enum にマッチしなくても動くようにフォールバック
            plan = plan_raw  # type: ignore[assignment]

        return TokenPayload(user_id=user_id, plan=plan)

    # ------------------------------------------------------------------
    # Port 実装 (TokenServicePort)
    # ------------------------------------------------------------------

    def issue_tokens(self, payload: TokenPayload) -> TokenPair:
        """
        Access / Refresh の 2 種類のトークンを発行し、
        それぞれの expires_at を持つ TokenPair を返す。
        """
        base_payload = {
            "sub": payload.user_id,
            # Enum の場合は .value、それ以外は str にフォールバック
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

        - 有効なトークンなら TokenPayload を返す。
        - 無効 / 期限切れなど JWT レベルのエラーは InvalidCredentialsError に包んで投げる。
          （/auth/me, get_current_user_dto などからドメインエラーとして扱いやすくするため）
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

        - 有効なトークンなら TokenPayload を返す。
        - 無効 / 期限切れなど JWTError はあえてここでは包まず、
          呼び出し側（RefreshTokenUseCase）で InvalidRefreshTokenError にまとめる。
        """
        claims = self._decode(token)  # JWTError はそのまま上に伝える
        return self._payload_from_claims(claims)
