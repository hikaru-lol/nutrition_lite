from __future__ import annotations

from typing import Callable

from sqlalchemy.orm import Session

from app.application.meal.ports.uow_port import MealUnitOfWorkPort
from app.application.meal.ports.food_entry_repository_port import FoodEntryRepositoryPort
from app.infra.db.session import create_session
from app.infra.db.repositories.food_entry_repository import SqlAlchemyFoodEntryRepository
from app.infra.db.uow.sqlalchemy_base import SqlAlchemyUnitOfWorkBase
# ↑ これは前回提案した共通ベース:
# app/infra/db/uow/sqlalchemy_base.py
# に置く想定


class SqlAlchemyMealUnitOfWork(SqlAlchemyUnitOfWorkBase, MealUnitOfWorkPort):
    """
    meal ドメイン用の Unit of Work 実装。

    - 1 UseCase 呼び出しごとに Session を開き、
      with ブロック終了時に commit / rollback / close を行う。
    """

    food_entry_repo: FoodEntryRepositoryPort

    def __init__(self, session_factory: Callable[[], Session] = create_session) -> None:
        super().__init__(session_factory)

    def _on_enter(self, session: Session) -> None:
        # この UoW 配下で使う Repository をここで組み立てる
        self.food_entry_repo = SqlAlchemyFoodEntryRepository(session)
