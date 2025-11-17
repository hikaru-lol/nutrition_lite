from __future__ import annotations

from typing import Protocol

from app.domain.auth.value_objects import HashedPassword


class PasswordHasherPort(Protocol):
    """
    パスワードのハッシュ / 検証のためのポート。
    """

    def hash(self, raw_password: str) -> HashedPassword:
        ...

    def verify(self, raw_password: str, hashed_password: HashedPassword) -> bool:
        ...
