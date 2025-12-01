from __future__ import annotations

from typing import Callable, Self

from sqlalchemy.orm import Session

from app.application.common.ports.unit_of_work_port import UnitOfWorkPort


class SqlAlchemyUnitOfWorkBase(UnitOfWorkPort):
    """
    SQLAlchemy ベースの共通 Unit of Work 実装。

    - Session の生成 / commit / rollback / close を共通化
    - サブクラスは `_on_enter(session)` でリポジトリを組み立てる
    """

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        assert self._session is not None, "Use UnitOfWork via 'with' block."
        return self._session

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        self._on_enter(self.session)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
        finally:
            self.session.close()
            self._session = None

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def _on_enter(self, session: Session) -> None:
        raise NotImplementedError
