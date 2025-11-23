from __future__ import annotations

from datetime import date
from typing import Protocol, runtime_checkable

from app.domain.auth.value_objects import UserId
from app.domain.target.entities import DailyTargetSnapshot


@runtime_checkable
class TargetSnapshotRepositoryPort(Protocol):
    """
    DailyTargetSnapshot の永続化用リポジトリポート。

    - 「その日付のターゲット値の凍結」を扱う
    """

    def add(self, snapshot: DailyTargetSnapshot) -> None:
        """
        新しい DailyTargetSnapshot を保存する。

        - 同一 (user_id, date) の重複は実装側で防ぐ or 上書きしないようにする
        """
        ...

    def get_by_user_and_date(
        self,
        user_id: UserId,
        snapshot_date: date,
    ) -> DailyTargetSnapshot | None:
        """
        指定ユーザー + 日付の Snapshot を 1件返す。

        - なければ None
        """
        ...

    def list_by_user(
        self,
        user_id: UserId,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DailyTargetSnapshot]:
        """
        ユーザーの DailyTargetSnapshot 一覧を返す。

        - start_date / end_date で範囲指定（どちらか片方だけでもOK）
        - 並び順は date ASC / DESC など実装側に任せてOK
        """
        ...
