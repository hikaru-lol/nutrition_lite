from __future__ import annotations

from typing import Protocol

from app.application.common.ports.unit_of_work_port import UnitOfWorkPort
from app.application.meal.ports.food_entry_repository_port import FoodEntryRepositoryPort


class MealUnitOfWorkPort(UnitOfWorkPort, Protocol):
    """
    meal ドメイン用の Unit of Work。

    - food_entry_repo を 1 トランザクションの中で扱うための UoW。
    """

    food_entry_repo: FoodEntryRepositoryPort
