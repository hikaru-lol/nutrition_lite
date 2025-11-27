from __future__ import annotations

from datetime import date as DateType

from app.application.target.ports.target_repository_port import (
    TargetRepositoryPort,
)
from app.application.target.ports.target_snapshot_repository_port import (
    TargetSnapshotRepositoryPort,
)
from app.domain.auth.value_objects import UserId
from app.domain.target.entities import (
    TargetDefinition,
    DailyTargetSnapshot,
)
from app.domain.target.errors import NoActiveTargetError  # 既存エラーに合わせて調整


class EnsureDailyTargetSnapshotUseCase:
    """
    指定した (user_id, date) の DailyTargetSnapshot を「必ず 1 つ用意する」UseCase。

    フロー:
        1. 既に DailyTargetSnapshot が存在するか？
            → あればそれを返す
        2. なければ、ユーザーのアクティブな TargetDefinition を取得
            → なければ ActiveTargetNotFoundError
        3. TargetDefinition から DailyTargetSnapshot を生成して保存
        4. 生成した Snapshot を返す
    """

    def __init__(
        self,
        target_repo: TargetRepositoryPort,
        snapshot_repo: TargetSnapshotRepositoryPort,
    ) -> None:
        self._target_repo = target_repo
        self._snapshot_repo = snapshot_repo

    def execute(
        self,
        user_id: UserId,
        date_: DateType,
    ) -> DailyTargetSnapshot:
        # --- 1. 既存 Snapshot チェック -------------------------------
        existing = self._snapshot_repo.get_by_user_and_date(
            user_id=user_id,
            date_=date_,
        )
        if existing is not None:
            return existing

        # --- 2. アクティブ TargetDefinition を取得 -------------------
        active_target: TargetDefinition | None = self._target_repo.get_active(
            user_id=user_id,
        )
        if active_target is None:
            raise NoActiveTargetError(
                f"Active TargetDefinition not found for user_id={user_id.value}"
            )

        # --- 3. TargetDefinition から Snapshot を生成 ----------------
        # Domain 側に用意しているファクトリメソッド名に合わせて調整してください。
        # 例: DailyTargetSnapshot.from_definition(...)
        snapshot = DailyTargetSnapshot.from_target(
            user_id=user_id,
            date=date_,
            definition=active_target,
        )

        # --- 4. 保存して返す ----------------------------------------
        self._snapshot_repo.add(snapshot)
        return snapshot
