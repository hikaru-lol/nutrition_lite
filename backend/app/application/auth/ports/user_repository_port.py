from __future__ import annotations

from typing import Protocol, Sequence

from app.domain.auth.entities import User
from app.domain.auth.value_objects import EmailAddress, UserId


class UserRepositoryPort(Protocol):
    """
    User 永続化のためのポート。
    """

    def get_by_id(self, user_id: UserId) -> User | None:
        ...

    def get_by_email(self, email: EmailAddress) -> User | None:
        ...

    def save(self, user: User) -> User:
        """
        新規 or 更新を抽象化。
        """
        ...

    def list_active_users(self) -> Sequence[User]:
        """
        提案生成対象となるアクティブユーザー一覧を返す。
        """
        raise NotImplementedError
