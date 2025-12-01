from __future__ import annotations

from app.application.meal.ports.uow_port import MealUnitOfWorkPort
from app.application.meal.ports.food_entry_repository_port import (
    FoodEntryRepositoryPort,
)


class FakeMealUnitOfWork(MealUnitOfWorkPort):
    """
    シンプルなメモリ上の Meal UoW。
    Repositories を共有しつつ with ブロックでトランザクションっぽく扱う。
    """

    def __init__(self, food_entry_repo: FoodEntryRepositoryPort) -> None:
        self.food_entry_repo = food_entry_repo
        self._committed = False

    def __enter__(self) -> "FakeMealUnitOfWork":
        self._committed = False
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type:
            self.rollback()
        else:
            self.commit()

    def commit(self) -> None:
        self._committed = True

    def rollback(self) -> None:  # pragma: no cover
        self._committed = False
