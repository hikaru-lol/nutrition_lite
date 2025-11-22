from __future__ import annotations

from datetime import date
from typing import Protocol

from app.domain.auth.value_objects import UserId
from app.domain.target.entities import DailyTargetSnapshot


class TargetSnapshotRepositoryPort(Protocol):
    """
    DailyTargetSnapshot の永続化を扱うポート。

    - 特定ユーザー・特定日付のスナップショット取得
    - 新規スナップショットの保存
    """

    def get_by_user_and_date(self, user_id: UserId, target_date: date) -> DailyTargetSnapshot | None:
        ...

    def save(self, snapshot: DailyTargetSnapshot) -> DailyTargetSnapshot:
        ...
