from __future__ import annotations

from datetime import date
from typing import Protocol, Sequence

from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.meal.value_objects import FoodEntryId, MealType


class FoodEntryRepositoryPort(Protocol):
    """
    FoodEntry 永続化用の Repository Port。

    実装例:
      - SqlAlchemyFoodEntryRepository
      - InMemoryFoodEntryRepository（テスト用） など
    """

    # --- 基本的な CRUD ----------------------------------------------

    def add(self, entry: FoodEntry) -> None:
        """新しい FoodEntry を永続化する。"""
        ...

    def update(self, entry: FoodEntry) -> None:
        """既存の FoodEntry を更新する。"""
        ...

    def delete(self, entry: FoodEntry) -> None:
        """FoodEntry を削除する（ソフト/ハードは実装側に委ねる）。"""
        ...

    def get_by_id(self, user_id: UserId, entry_id: FoodEntryId) -> FoodEntry | None:
        """
        指定したユーザーの FoodEntry を ID で取得する。

        - 他ユーザーのデータを誤って取得しないよう、user_id も引数に含める。
        """
        ...

    # --- 検索系 ------------------------------------------------------

    def list_by_user_and_date(self, user_id: UserId, target_date: date) -> Sequence[FoodEntry]:
        """
        指定したユーザーの、ある1日分の FoodEntry 一覧を取得する。
        main / snack を区別せず、その日の全ての FoodEntry を返す。
        """
        ...

    def list_by_user_date_type_index(
        self,
        user_id: UserId,
        target_date: date,
        meal_type: MealType,
        meal_index: int | None,
    ) -> Sequence[FoodEntry]:
        """
        指定したユーザーの、ある1回分の食事に対応する FoodEntry 一覧を取得する。

        - meal_type == main の場合:
            meal_index は 1 以上の整数を指定し、
            「その日の N 回目のメインの食事」に含まれる全 FoodEntry を返す。
        - meal_type == snack の場合:
            meal_index には None を渡し、
            「その日の snack 全体」を返す、などのポリシーで実装する想定。
            （詳細な扱いは UseCase/設計次第で調整可能）
        """
        ...
