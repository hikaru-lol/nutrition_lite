from __future__ import annotations

from typing import Dict

from app.application.profile.ports.profile_repository_port import ProfileRepositoryPort
from app.domain.profile.entities import Profile
from app.domain.auth.value_objects import UserId


class InMemoryProfileRepository(ProfileRepositoryPort):
    """
    テスト用のインメモリ ProfileRepository 実装。

    - Postgres なしで UseCase / API テストを回すための Fake。
    """

    def __init__(self) -> None:
        # key: user_id.value, value: Profile
        self._profiles: Dict[str, Profile] = {}

    def get_by_user_id(self, user_id: UserId) -> Profile | None:
        return self._profiles.get(user_id.value)

    def save(self, profile: Profile) -> Profile:
        self._profiles[profile.user_id.value] = profile
        return profile

    # テスト専用: 状態リセット用
    def clear(self) -> None:
        self._profiles.clear()
