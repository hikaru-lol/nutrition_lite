from __future__ import annotations

from app.application.auth.ports.uow_port import AuthUnitOfWorkPort
from app.application.auth.ports.user_repository_port import UserRepositoryPort
from tests.fakes.auth_repositories import InMemoryUserRepository


class FakeAuthUnitOfWork(AuthUnitOfWorkPort):
    def __init__(self, user_repo: InMemoryUserRepository | None = None) -> None:
        self.user_repo: UserRepositoryPort = user_repo or InMemoryUserRepository()
        self._committed = False

    def __enter__(self) -> "FakeAuthUnitOfWork":
        self._committed = False
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        # エラーが出たときの rollback の振る舞いが必要ならここで user_repo をリセットするなど
        pass

    def commit(self) -> None:
        self._committed = True

    def rollback(self) -> None:
        self._committed = False
