from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.application.auth.ports.password_hasher_port import PasswordHasherPort
from app.application.auth.ports.token_service_port import (
    TokenServicePort,
    TokenPayload,
    TokenPair,
)
from app.application.auth.ports.clock_port import ClockPort
from app.domain.auth.value_objects import HashedPassword, UserPlan


class FakePasswordHasher(PasswordHasherPort):
    """
    超シンプルなハッシュ実装。
    セキュリティ目的ではなく「同じ入力なら同じハッシュになる」ことだけを保証。
    """

    def hash(self, raw_password: str) -> HashedPassword:
        # HashedPassword が VO でも NewType でも動くように、value 引数 1 個の想定で生成
        # type: ignore[call-arg]
        return HashedPassword(f"hashed:{raw_password}")

    def verify(self, raw_password: str, hashed_password: HashedPassword) -> bool:
        # HashedPassword に value 属性がある場合はそれを使う
        stored = getattr(hashed_password, "value", str(hashed_password))
        return stored == f"hashed:{raw_password}"


class FakeTokenService(TokenServicePort):
    """
    JWT を使わず、シンプルな文字列ベースのトークンを発行する Fake 実装。

    トークン形式:
      access:{user_id}:{plan_value}
      refresh:{user_id}:{plan_value}

    有効期限は TokenPair に入れるが、verify ではチェックしない。
    （期限切れテストをしたくなったら拡張すればOK）
    """

    def __init__(
        self,
        access_ttl: timedelta | None = None,
        refresh_ttl: timedelta | None = None,
    ) -> None:
        self._access_ttl = access_ttl or timedelta(minutes=15)
        self._refresh_ttl = refresh_ttl or timedelta(days=7)

    # --- ヘルパー -------------------------------------------------

    @staticmethod
    def _plan_to_str(plan: UserPlan) -> str:
        # Enum(UserPlan.TRIAL) でも value object でも動くように value 属性を優先
        return getattr(plan, "value", str(plan))

    @staticmethod
    def _plan_from_str(plan_str: str) -> UserPlan:
        """
        UserPlan が Enum でも VO でも動くよう、
        まず UserPlan(plan_str) を試し、無理なら素の文字列を返す。
        """
        try:
            return UserPlan(plan_str)  # type: ignore[call-arg]
        except Exception:
            return plan_str  # type: ignore[return-value]

    def _build_token(self, kind: str, payload: TokenPayload) -> str:
        plan_str = self._plan_to_str(payload.plan)
        return f"{kind}:{payload.user_id}:{plan_str}"

    def _parse_token(self, token: str, expected_kind: str) -> TokenPayload:
        prefix = f"{expected_kind}:"
        if not token.startswith(prefix):
            raise ValueError("Invalid token prefix")

        parts = token.split(":", 2)
        if len(parts) != 3:
            raise ValueError("Invalid token format")

        _, user_id, plan_str = parts
        plan = self._plan_from_str(plan_str)
        return TokenPayload(user_id=user_id, plan=plan)

    # --- Port 実装 -------------------------------------------------

    def issue_tokens(self, payload: TokenPayload) -> TokenPair:
        now = datetime.now(timezone.utc)

        access_token = self._build_token("access", payload)
        refresh_token = self._build_token("refresh", payload)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_at=now + self._access_ttl,
            refresh_expires_at=now + self._refresh_ttl,
        )

    def verify_access_token(self, token: str) -> TokenPayload:
        return self._parse_token(token, "access")

    def verify_refresh_token(self, token: str) -> TokenPayload:
        return self._parse_token(token, "refresh")


class FixedClock(ClockPort):
    """
    テスト用の固定時計。
    now() の値を固定したり、任意に進めたりできる。
    """

    def __init__(self) -> None:
        self._now = datetime(2024, 1, 1, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._now

    def advance(self, delta: timedelta) -> None:
        self._now += delta

    def reset(self) -> None:
        self._now = datetime(2024, 1, 1, tzinfo=timezone.utc)
