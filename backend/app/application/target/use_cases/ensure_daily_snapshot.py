from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone

from app.application.target.errors import TargetNotFoundError
from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.target.entities import DailyTargetSnapshot
from app.domain.target.value_objects import TargetId  # 型参照だけならなくてもよいが、明示のため


@dataclass(slots=True)
class EnsureDailySnapshotInputDTO:
    """
    DailyTargetSnapshot を「その日付について必ず1件存在する状態」にするための入力 DTO。

    - date を省略した場合は今日の日付を使う想定。
    """

    user_id: str
    target_date: date | None = None


class EnsureDailySnapshotUseCase:
    """
    指定ユーザー + 日付について DailyTargetSnapshot を「存在させる」ユースケース。

    ロジック:
      1. (user_id, date) の Snapshot が既にあれば、それをそのまま返す
      2. なければ、その時点で Active な TargetDefinition を取得
      3. Active Target がなければ TargetNotFoundError
      4. TargetDefinition から DailyTargetSnapshot を生成し、保存して返す
    """

    def __init__(self, uow: TargetUnitOfWorkPort) -> None:
        self._uow = uow

    def execute(
        self,
        input_dto: EnsureDailySnapshotInputDTO,
    ) -> DailyTargetSnapshot:
        target_date = input_dto.target_date or date.today()
        user_id = UserId(input_dto.user_id)

        with self._uow as uow:
            existing = uow.target_snapshot_repo.get_by_user_and_date(
                user_id=user_id,
                snapshot_date=target_date,
            )
            if existing is not None:
                return existing

            active_target = uow.target_repo.get_active(user_id)
            if active_target is None:
                raise TargetNotFoundError(
                    "Cannot create DailyTargetSnapshot because no active target exists."
                )

            snapshot = DailyTargetSnapshot.from_target(
                target=active_target,
                snapshot_date=target_date,
                created_at=datetime.now(timezone.utc),
            )

            uow.target_snapshot_repo.add(snapshot)
            uow.commit()

            return snapshot
