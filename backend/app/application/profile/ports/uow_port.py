from __future__ import annotations

from typing import Protocol

from app.application.profile.ports.profile_repository_port import ProfileRepositoryPort


class ProfileUnitOfWorkPort(Protocol):
    """
    profile ドメイン用の Unit of Work。

    1ユースケース = 1トランザクション を前提に、
    with ブロックのスコープでトランザクションを管理する。
    """

    profile_repo: ProfileRepositoryPort

    def __enter__(self) -> "ProfileUnitOfWorkPort":
        ...

    def __exit__(self, exc_type, exc, tb) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
