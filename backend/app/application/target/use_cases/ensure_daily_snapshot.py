from __future__ import annotations

from app.application.target.dto.target_dto import EnsureDailySnapshotInputDTO
from app.application.target.errors import TargetNotFoundError
from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.target.entities import DailyTargetSnapshot
from app.domain.target.errors import NoActiveTargetError


class EnsureDailyTargetSnapshotUseCase:
    """
    指定した (user_id, date) の DailyTargetSnapshot を「必ず 1 つ用意する」UseCase。

    フロー:
        1. 既に DailyTargetSnapshot が存在するか？
            → あればそれを返す
        2. なければ、ユーザーのアクティブな TargetDefinition を取得
            → なければ TargetNotFoundError
        3. TargetDefinition から DailyTargetSnapshot を生成して保存
        4. 生成した Snapshot を返す
    """

    def __init__(self, uow: TargetUnitOfWorkPort) -> None:
        self._uow = uow

    def execute(
        self,
        input_dto: EnsureDailySnapshotInputDTO,
    ) -> DailyTargetSnapshot:
        user_id = UserId(input_dto.user_id)
        snapshot_date = input_dto.target_date

        with self._uow as uow:
            # --- 1. 既存 Snapshot チェック -------------------------------
            existing = uow.target_snapshot_repo.get_by_user_and_date(
                user_id=user_id,
                snapshot_date=snapshot_date,
            )
            if existing is not None:
                return existing

            # --- 2. アクティブ TargetDefinition を取得 -------------------
            active_target = uow.target_repo.get_active(user_id=user_id)
            if active_target is None:
                raise TargetNotFoundError(
                    "Active TargetDefinition not found for the current user."
                )

            # --- 3. TargetDefinition から Snapshot を生成 ----------------
            snapshot = DailyTargetSnapshot.from_target(
                target=active_target,
                snapshot_date=snapshot_date,
            )

            # --- 4. 保存して返す ----------------------------------------
            uow.target_snapshot_repo.add(snapshot)
            return snapshot
