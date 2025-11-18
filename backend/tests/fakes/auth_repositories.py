from __future__ import annotations

from typing import Dict

from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.domain.auth.entities import User
from app.domain.auth.value_objects import EmailAddress, UserId


class InMemoryUserRepository(UserRepositoryPort):
    """
    テスト用のインメモリ UserRepository 実装。
    Postgres なしでユースケース／API テストを回すための Fake。
    """

    def __init__(self) -> None:
        # UserId/EmailAddress は VO なので、内側では str(value) で管理する
        self._users_by_id: Dict[str, User] = {}
        self._users_by_email: Dict[str, User] = {}

    def get_by_id(self, user_id: UserId) -> User | None:
        """
        UserId.value をキーにユーザーを取得する。
        （論理削除ユーザーを除外するかどうかは、本番実装に合わせて必要なら拡張）
        """
        return self._users_by_id.get(getattr(user_id, "value", str(user_id)))

    def get_by_email(self, email: EmailAddress) -> User | None:
        key = getattr(email, "value", str(email))
        return self._users_by_email.get(key)

    def save(self, user: User) -> User:
        """
        新規 or 更新を同じメソッドで扱う。
        """
        id_key = getattr(user.id, "value", str(user.id))
        email_key = getattr(user.email, "value", str(user.email))

        self._users_by_id[id_key] = user
        self._users_by_email[email_key] = user
        return user

    # 🔸テスト専用: 状態リセット用ヘルパー
    def clear(self) -> None:
        self._users_by_id.clear()
        self._users_by_email.clear()
