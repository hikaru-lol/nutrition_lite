from __future__ import annotations

from typing import Protocol

from app.application.auth.ports.user_repository_port import UserRepositoryPort


class AuthUnitOfWorkPort(Protocol):
    """
    auth ドメイン用の Unit of Work。

    1ユースケース = 1トランザクション を前提に、
    with ブロックのスコープでトランザクションを管理する。
    """

    user_repo: UserRepositoryPort

    def __enter__(self) -> "AuthUnitOfWorkPort":
        ...

    def __exit__(self, exc_type, exc, tb) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
