from __future__ import annotations

from typing import Protocol

from app.application.common.ports.unit_of_work_port import UnitOfWorkPort
from app.application.target.ports.target_repository_port import TargetRepositoryPort
from app.application.target.ports.target_snapshot_repository_port import (
    TargetSnapshotRepositoryPort,
)


class TargetUnitOfWorkPort(UnitOfWorkPort, Protocol):
    """
    Target 関連のユースケースで使用する Unit of Work ポート。
    """
    target_repo: TargetRepositoryPort
    target_snapshot_repo: TargetSnapshotRepositoryPort
