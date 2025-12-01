from __future__ import annotations

from datetime import datetime, date
from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import Session

from app.application.meal.ports.food_entry_repository_port import FoodEntryRepositoryPort
from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.meal.errors import FoodEntryNotFoundError
from app.domain.meal.value_objects import FoodEntryId, MealType
from app.infra.db.models.meal import FoodEntryModel


class SqlAlchemyFoodEntryRepository(FoodEntryRepositoryPort):
    """
    FoodEntryRepositoryPort の SQLAlchemy 実装。

    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # --- Entity <-> Model 変換 ----------------------------------------

    def _to_entity(self, model: FoodEntryModel) -> FoodEntry:
        return FoodEntry(
            id=FoodEntryId(model.id),
            user_id=UserId(str(model.user_id)),
            date=model.date,
            meal_type=MealType(model.meal_type),
            meal_index=model.meal_index,
            name=model.name,
            amount_value=model.amount_value,
            amount_unit=model.amount_unit,
            serving_count=model.serving_count,
            note=model.note,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    def _from_entity(self, entry: FoodEntry) -> FoodEntryModel:
        return FoodEntryModel(
            id=entry.id.value,
            user_id=UUID(entry.user_id.value),
            date=entry.date,
            meal_type=entry.meal_type.value,
            meal_index=entry.meal_index,
            name=entry.name,
            amount_value=entry.amount_value,
            amount_unit=entry.amount_unit,
            serving_count=entry.serving_count,
            note=entry.note,
            created_at=entry.created_at or datetime.utcnow(),
            updated_at=entry.updated_at or datetime.utcnow(),
            deleted_at=entry.deleted_at,
        )

    # --- CRUD ---------------------------------------------------------

    def add(self, entry: FoodEntry) -> None:
        model = self._from_entity(entry)
        self._session.add(model)

    def update(self, entry: FoodEntry) -> None:
        """
        既存行を更新する。

        - user_id も条件に含めて、他ユーザーのデータを誤更新しないようにする。
        """
        model = (
            self._session.query(FoodEntryModel)
            .filter(
                FoodEntryModel.id == entry.id.value,
                FoodEntryModel.user_id == UUID(entry.user_id.value),
                FoodEntryModel.deleted_at.is_(None),
            )
            .one_or_none()
        )
        if model is None:
            raise FoodEntryNotFoundError(
                f"FoodEntry not found for id={entry.id} user_id={entry.user_id}"
            )

        model.date = entry.date
        model.meal_type = entry.meal_type.value
        model.meal_index = entry.meal_index
        model.name = entry.name
        model.amount_value = entry.amount_value
        model.amount_unit = entry.amount_unit
        model.serving_count = entry.serving_count
        model.note = entry.note
        model.updated_at = datetime.utcnow()

    def delete(self, entry: FoodEntry) -> None:
        """
        ソフトデリート。

        - deleted_at に現在時刻をセット
        """
        model = (
            self._session.query(FoodEntryModel)
            .filter(
                FoodEntryModel.id == entry.id.value,
                FoodEntryModel.user_id == UUID(entry.user_id.value),
                FoodEntryModel.deleted_at.is_(None),
            )
            .one_or_none()
        )
        if model is None:
            # 既に削除済みなら何もしない（冪等性のため）
            return

        model.deleted_at = datetime.utcnow()

    # --- 検索 ---------------------------------------------------------

    def get_by_id(self, user_id: UserId, entry_id: FoodEntryId) -> FoodEntry | None:
        model = (
            self._session.query(FoodEntryModel)
            .filter(
                FoodEntryModel.id == entry_id.value,
                FoodEntryModel.user_id == UUID(user_id.value),
                FoodEntryModel.deleted_at.is_(None),
            )
            .one_or_none()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def list_by_user_and_date(
        self,
        user_id: UserId,
        target_date: date,
    ) -> Sequence[FoodEntry]:
        models: Sequence[FoodEntryModel] = (
            self._session.query(FoodEntryModel)
            .filter(
                FoodEntryModel.user_id == UUID(user_id.value),
                FoodEntryModel.date == target_date,
                FoodEntryModel.deleted_at.is_(None),
            )
            .order_by(
                FoodEntryModel.date.asc(),
                FoodEntryModel.meal_type.asc(),
                FoodEntryModel.meal_index.asc().nulls_last(),
                FoodEntryModel.created_at.asc(),
            )
            .all()
        )
        return [self._to_entity(m) for m in models]

    def list_by_user_date_type_index(
        self,
        user_id: UserId,
        target_date: date,
        meal_type: MealType,
        meal_index: int | None,
    ) -> Sequence[FoodEntry]:
        q = (
            self._session.query(FoodEntryModel)
            .filter(
                FoodEntryModel.user_id == UUID(user_id.value),
                FoodEntryModel.date == target_date,
                FoodEntryModel.meal_type == meal_type.value,
                FoodEntryModel.deleted_at.is_(None),
            )
        )

        # main のときは meal_index で絞る
        if meal_type == MealType.MAIN:
            q = q.filter(FoodEntryModel.meal_index == meal_index)
        # snack のときは meal_index で絞らない（その日の snack 全体、など）

        models: Sequence[FoodEntryModel] = q.order_by(
            FoodEntryModel.created_at.asc()
        ).all()

        return [self._to_entity(m) for m in models]
