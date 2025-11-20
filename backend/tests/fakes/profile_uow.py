from __future__ import annotations

from app.application.profile.ports.uow_port import ProfileUnitOfWorkPort
from app.application.profile.ports.profile_repository_port import ProfileRepositoryPort
from tests.fakes.profile_repositories import InMemoryProfileRepository


class FakeProfileUnitOfWork(ProfileUnitOfWorkPort):
    """
    テスト用の ProfileUnitOfWorkPort 実装。

    - トランザクション管理はダミー（commit/rollback はフラグを持つだけ）。
    - profile_repo に InMemoryProfileRepository を持つ。
    """

    def __init__(self, profile_repo: InMemoryProfileRepository | None = None) -> None:
        self.profile_repo: ProfileRepositoryPort = profile_repo or InMemoryProfileRepository()
        self._committed = False

    def __enter__(self) -> "FakeProfileUnitOfWork":
        self._committed = False
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        # 本番の UoW のような commit/rollback はここでは何もしない
        pass

    def commit(self) -> None:
        self._committed = True

    def rollback(self) -> None:
        self._committed = False

    # テスト用にコミットされたかどうか見たい場合に使える（使わなくてもOK）
    @property
    def committed(self) -> bool:
        return self._committed
