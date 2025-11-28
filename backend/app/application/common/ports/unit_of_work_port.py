from __future__ import annotations

from typing import Protocol, Self, runtime_checkable


@runtime_checkable
class UnitOfWorkPort(Protocol):
    """
    共通の Unit of Work ポート。

    - 1ユースケース = 1トランザクション
    - with ブロックのスコープでトランザクションを管理する
    """

    def __enter__(self) -> Self:
        ...

    def __exit__(self, exc_type, exc, tb) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
