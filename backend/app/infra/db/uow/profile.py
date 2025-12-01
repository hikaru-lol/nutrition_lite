from __future__ import annotations

from typing import Callable

from sqlalchemy.orm import Session

from app.application.profile.ports.uow_port import ProfileUnitOfWorkPort
from app.application.profile.ports.profile_repository_port import ProfileRepositoryPort
from app.infra.db.session import create_session
from app.infra.db.repositories.profile_repository import SqlAlchemyProfileRepository
from app.infra.db.uow.sqlalchemy_base import SqlAlchemyUnitOfWorkBase


class SqlAlchemyProfileUnitOfWork(SqlAlchemyUnitOfWorkBase, ProfileUnitOfWorkPort):
    profile_repo: ProfileRepositoryPort

    def __init__(self, session_factory: Callable[[], Session] = create_session) -> None:
        super().__init__(session_factory)

    def _on_enter(self, session: Session) -> None:
        self.profile_repo = SqlAlchemyProfileRepository(session)
