from __future__ import annotations

from typing import Callable

from sqlalchemy.orm import Session

from app.application.auth.ports.uow_port import AuthUnitOfWorkPort
from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.infra.db.session import create_session
from app.infra.db.repositories.user_repository import SqlAlchemyUserRepository
from app.infra.db.uow.sqlalchemy_base import SqlAlchemyUnitOfWorkBase


class SqlAlchemyAuthUnitOfWork(SqlAlchemyUnitOfWorkBase, AuthUnitOfWorkPort):
    user_repo: UserRepositoryPort

    def __init__(self, session_factory: Callable[[], Session] = create_session) -> None:
        super().__init__(session_factory)

    def _on_enter(self, session: Session) -> None:
        self.user_repo = SqlAlchemyUserRepository(session)
