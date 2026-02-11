"""チュートリアル機能のUnit of Work実装"""

from __future__ import annotations

from typing import Callable

from sqlalchemy.orm import Session

from app.application.tutorial.ports.tutorial_unit_of_work_port import TutorialUnitOfWorkPort
from app.infra.db.repositories.tutorial_repository import SqlAlchemyTutorialRepository
from app.infra.db.uow.sqlalchemy_base import SqlAlchemyUnitOfWorkBase


class SqlAlchemyTutorialUnitOfWork(SqlAlchemyUnitOfWorkBase, TutorialUnitOfWorkPort):
    """SQLAlchemy実装のTutorial Unit of Work"""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        super().__init__(session_factory)
        self.tutorial_repo: SqlAlchemyTutorialRepository

    def _on_enter(self, session: Session) -> None:
        """セッション開始時にリポジトリを初期化"""
        self.tutorial_repo = SqlAlchemyTutorialRepository(session)