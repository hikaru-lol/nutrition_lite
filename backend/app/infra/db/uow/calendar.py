from typing import Callable
from sqlalchemy.orm import Session
from app.application.calendar.ports.calendar_unit_of_work_port import CalendarUnitOfWorkPort
from app.infra.db.repositories.calendar_repository import SqlAlchemyCalendarRepository
from app.infra.db.uow.sqlalchemy_base import SqlAlchemyUnitOfWorkBase
from app.infra.db.session import create_session


class SqlAlchemyCalendarUnitOfWork(SqlAlchemyUnitOfWorkBase, CalendarUnitOfWorkPort):
    """SQLAlchemy を使ったカレンダー Unit of Work 実装"""

    def __init__(self, session_factory: Callable[[], Session] = create_session) -> None:
        super().__init__(session_factory)

    def _on_enter(self, session: Session) -> None:
        """セッション開始時にリポジトリを初期化"""
        self.calendar_repo = SqlAlchemyCalendarRepository(session)
