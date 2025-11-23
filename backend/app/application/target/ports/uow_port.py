from __future__ import annotations

from typing import Protocol, runtime_checkable, Self

from app.application.target.ports.target_repository_port import TargetRepositoryPort
from app.application.target.ports.target_snapshot_repository_port import (
    TargetSnapshotRepositoryPort,
)


@runtime_checkable
class TargetUnitOfWorkPort(Protocol):
    """
    Target 関連のユースケースで使用する Unit of Work ポート。

    - DB セッションと複数のリポジトリを束ねる
    - コンテキストマネージャとして使うことを前提とする:

        with uow as tx:
            target = tx.target_repo.get_by_id(...)
            ...
            tx.commit()
    """

    # UoW が提供するリポジトリ
    target_repo: TargetRepositoryPort
    target_snapshot_repo: TargetSnapshotRepositoryPort

    # --- Context manager -----------------------------------------------

    def __enter__(self) -> Self:
        ...

    def __exit__(self, exc_type, exc, tb) -> None:
        """
        - 例外が発生していなければ commit() する
        - 例外が発生していれば rollback() する
        """

    # --- Transaction control -------------------------------------------

    def commit(self) -> None:
        """現在のトランザクションをコミットする。"""
        ...

    def rollback(self) -> None:
        """現在のトランザクションをロールバックする。"""
        ...
