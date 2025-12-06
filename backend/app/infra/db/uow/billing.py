from __future__ import annotations

from typing import Callable

from sqlalchemy.orm import Session

from app.application.billing.ports.uow_port import BillingUnitOfWorkPort
from app.application.billing.ports.billing_repository_port import BillingRepositoryPort
from app.infra.db.session import create_session
from app.infra.db.repositories.billing_account_repository import (
    SqlAlchemyBillingAccountRepository,
)
from app.infra.db.uow.sqlalchemy_base import SqlAlchemyUnitOfWorkBase


class SqlAlchemyBillingUnitOfWork(SqlAlchemyUnitOfWorkBase, BillingUnitOfWorkPort):
    """
    Billing ドメイン用の Unit of Work 実装。

    - 1 UseCase 呼び出しごとに新しい Session を開き、
      with ブロックの終了時に commit/rollback を行う。
    """

    billing_repo: BillingRepositoryPort

    def __init__(self, session_factory: Callable[[], Session] = create_session) -> None:
        super().__init__(session_factory)

    def _on_enter(self, session: Session) -> None:
        self.billing_repo = SqlAlchemyBillingAccountRepository(session)
