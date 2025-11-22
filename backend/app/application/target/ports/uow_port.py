from __future__ import annotations

from typing import Protocol

from app.application.target.ports.target_repository_port import TargetRepositoryPort
from app.application.target.ports.target_snapshot_repository_port import TargetSnapshotRepositoryPort


class TargetUnitOfWorkPort(Protocol):
    """
    target ドメイン用の Unit of Work。

    1ユースケース = 1トランザクションを前提に、
    with ブロックのスコープで Target / Snapshot の操作をまとめて管理する。
    """

    target_repo: TargetRepositoryPort
    snapshot_repo: TargetSnapshotRepositoryPort

    def __enter__(self) -> "TargetUnitOfWorkPort":
        ...

    def __exit__(self, exc_type, exc, tb) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
