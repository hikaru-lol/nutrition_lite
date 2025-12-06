from __future__ import annotations

from typing import Protocol, runtime_checkable, Self

from app.application.billing.ports.billing_repository_port import BillingRepositoryPort


@runtime_checkable
class BillingUnitOfWorkPort(Protocol):
    """
    Billing ドメイン用の Unit of Work ポート。

    - BillingAccountRepository をまとめて扱う。
    - 1 UseCase = 1 トランザクション、という前提。
    """

    billing_repo: BillingRepositoryPort

    def __enter__(self) -> Self:
        ...

    def __exit__(self, exc_type, exc, tb) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
