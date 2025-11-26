from __future__ import annotations

from uuid import UUID

from app.application.meal.ports.food_entry_repository_port import (
    FoodEntryRepositoryPort,
)
from app.domain.auth.value_objects import UserId
from app.domain.meal.errors import FoodEntryNotFoundError
from app.domain.meal.value_objects import FoodEntryId
from app.application.meal.dto.food_entry_dto import DeleteFoodEntryResultDTO


class DeleteFoodEntryUseCase:
    """
    FoodEntry を削除する UseCase。

    - Repository 実装ではソフトデリート（deleted_at セット）想定。
    """

    def __init__(self, repo: FoodEntryRepositoryPort) -> None:
        self._repo = repo

    def execute(self, user_id: UserId, entry_id_str: str) -> DeleteFoodEntryResultDTO:
        entry_id = FoodEntryId(UUID(entry_id_str))

        existing = self._repo.get_by_id(user_id, entry_id)
        if existing is None:
            # NotFound を明示的にドメインエラーで表現
            raise FoodEntryNotFoundError(
                f"FoodEntry not found for id={entry_id_str} user_id={user_id.value}"
            )

        # 削除対象の date を保持
        deleted_date = existing.date

        self._repo.delete(existing)
        # 2回目以降の呼び出しは Repository 側で no-op として冪等性を担保

        # 削除された日の情報だけ返す
        return DeleteFoodEntryResultDTO(date=deleted_date)
