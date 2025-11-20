from __future__ import annotations

from typing import Callable

from sqlalchemy.orm import Session

from app.application.auth.ports.uow_port import AuthUnitOfWorkPort
from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.infra.db.session import create_session
from app.infra.db.repositories.user_repository import SqlAlchemyUserRepository
from app.application.profile.ports.uow_port import ProfileUnitOfWorkPort
from app.application.profile.ports.profile_repository_port import ProfileRepositoryPort
from app.infra.db.repositories.profile_repository import SqlAlchemyProfileRepository


class SqlAlchemyAuthUnitOfWork(AuthUnitOfWorkPort):
    """
    auth 用の SQLAlchemy ベースの Unit of Work 実装。
    """

    def __init__(self, session_factory: Callable[[], Session] = create_session) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self.user_repo: UserRepositoryPort  # type: ignore[assignment]

    def __enter__(self) -> "SqlAlchemyAuthUnitOfWork":
        self._session = self._session_factory()
        # この Session に紐づく UserRepository を組み立てる
        self.user_repo = SqlAlchemyUserRepository(self._session)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        assert self._session is not None
        try:
            if exc_type is None:
                self._session.commit()
            else:
                self._session.rollback()
        finally:
            self._session.close()
            self._session = None  # GC しやすく

    def commit(self) -> None:
        assert self._session is not None
        self._session.commit()

    def rollback(self) -> None:
        assert self._session is not None
        self._session.rollback()


class SqlAlchemyProfileUnitOfWork(ProfileUnitOfWorkPort):
    """
    profile ドメイン用の Unit of Work。

    - 1 UseCase = 1 DB トランザクション。
    - profile_repo が SQLAlchemy セッションにひもづく。
    """

    def __init__(self, session_factory: Callable[[], Session] = create_session) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self.profile_repo: ProfileRepositoryPort  # type: ignore[assignment]

    def __enter__(self) -> "SqlAlchemyProfileUnitOfWork":
        self._session = self._session_factory()
        self.profile_repo = SqlAlchemyProfileRepository(self._session)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        assert self._session is not None
        try:
            if exc_type is None:
                self._session.commit()
            else:
                self._session.rollback()
        finally:
            self._session.close()
            self._session = None

    def commit(self) -> None:
        assert self._session is not None
        self._session.commit()

    def rollback(self) -> None:
        assert self._session is not None
        self._session.rollback()
