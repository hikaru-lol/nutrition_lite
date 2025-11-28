from __future__ import annotations

from typing import Callable

from sqlalchemy.orm import Session

from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.application.target.ports.target_repository_port import TargetRepositoryPort
from app.application.target.ports.target_snapshot_repository_port import (
    TargetSnapshotRepositoryPort,
)
from app.infra.db.session import create_session
from app.infra.db.repositories.target_repository import SqlAlchemyTargetRepository
from app.infra.db.repositories.target_snapshot_repository import (
    SqlAlchemyTargetSnapshotRepository,
)
from app.infra.db.uow.sqlalchemy_base import SqlAlchemyUnitOfWorkBase


class SqlAlchemyTargetUnitOfWork(SqlAlchemyUnitOfWorkBase, TargetUnitOfWorkPort):
    target_repo: TargetRepositoryPort
    target_snapshot_repo: TargetSnapshotRepositoryPort

    def __init__(self, session_factory: Callable[[], Session] = create_session) -> None:
        super().__init__(session_factory)

    def _on_enter(self, session: Session) -> None:
        self.target_repo = SqlAlchemyTargetRepository(session)
        self.target_snapshot_repo = SqlAlchemyTargetSnapshotRepository(session)
