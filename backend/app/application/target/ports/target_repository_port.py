from __future__ import annotations

from typing import Protocol

from app.domain.auth.value_objects import UserId
from app.domain.target.entities import TargetDefinition
from app.domain.target.value_objects import TargetId


class TargetRepositoryPort(Protocol):
    """
    TargetDefinition の永続化を扱うポート。

    - ユーザーごとのターゲット一覧の取得
    - アクティブターゲットの取得
    - 新規 / 更新の保存
    """

    def list_for_user(self, user_id: UserId) -> list[TargetDefinition]:
        ...

    def get_by_id(self, user_id: UserId, target_id: TargetId) -> TargetDefinition | None:
        ...

    def get_active_for_user(self, user_id: UserId) -> TargetDefinition | None:
        ...

    def count_for_user(self, user_id: UserId) -> int:
        ...

    def save(self, target: TargetDefinition) -> TargetDefinition:
        """
        新規 / 更新どちらもこのメソッドで扱う。
        """
        ...
