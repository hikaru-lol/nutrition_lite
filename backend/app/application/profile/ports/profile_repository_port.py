from __future__ import annotations

from typing import Protocol

from app.domain.auth.value_objects import UserId
from app.domain.profile.entities import Profile


class ProfileRepositoryPort(Protocol):
    """
    Profile 永続化のためのポート。
    """

    def get_by_user_id(self, user_id: UserId) -> Profile | None:
        """
        user_id に紐づく Profile を返す。
        存在しなければ None。
        """
        ...

    def save(self, profile: Profile) -> Profile:
        """
        新規 or 更新を抽象化。
        """
        ...
