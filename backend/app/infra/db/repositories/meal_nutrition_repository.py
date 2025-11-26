from __future__ import annotations

from datetime import date
from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from app.application.nutrition.ports.meal_nutrition_repository_port import (
    MealNutritionSummaryRepositoryPort,
)
from app.domain.auth.value_objects import UserId
from app.domain.meal.value_objects import MealType
from app.domain.nutrition.meal_nutrition import (
    MealNutritionSummary,
    MealNutritionSummaryId,
    MealNutrientIntake,
)
from app.domain.target.value_objects import NutrientCode, NutrientAmount, NutrientSource
from app.infra.db.models.meal_nutrition import (
    MealNutritionSummaryModel,
    MealNutritionNutrientModel,
)


class SqlAlchemyMealNutritionSummaryRepository(MealNutritionSummaryRepositoryPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    # --- Entity <-> Model 変換 ----------------------------------------

    def _to_entity(self, model: MealNutritionSummaryModel) -> MealNutritionSummary:
        nutrients: list[MealNutrientIntake] = []
        for n in model.nutrients:
            nutrients.append(
                MealNutrientIntake(
                    code=NutrientCode(n.code),
                    amount=NutrientAmount(
                        value=n.amount_value, unit=n.amount_unit),
                    source=NutrientSource(n.source),
                )
            )

        return MealNutritionSummary(
            id=MealNutritionSummaryId(model.id),
            user_id=UserId(str(model.user_id)),
            date=model.date,
            meal_type=MealType(model.meal_type),
            meal_index=model.meal_index,
            nutrients=nutrients,
            generated_at=model.generated_at,
        )

    def _apply_entity_to_model(
        self,
        entity: MealNutritionSummary,
        model: MealNutritionSummaryModel,
    ) -> None:
        model.user_id = UUID(entity.user_id.value)
        model.date = entity.date
        model.meal_type = entity.meal_type.value
        model.meal_index = entity.meal_index
        # generated_at は基本的に作成時の値を維持したいので更新しない

        # nutrients: いったん全部消して入れ直すシンプル実装
        model.nutrients.clear()
        for n in entity.nutrients:
            model.nutrients.append(
                MealNutritionNutrientModel(
                    summary_id=model.id,
                    code=n.code.value,
                    amount_value=n.amount.value,
                    amount_unit=n.amount.unit,
                    source=n.source.value,
                )
            )

    # --- Port 実装 -----------------------------------------------------

    def get_by_user_date_meal(
        self,
        *,
        user_id: UserId,
        target_date: date,
        meal_type: MealType,
        meal_index: int | None,
    ) -> MealNutritionSummary | None:
        model = (
            self._session.query(MealNutritionSummaryModel)
            .options(selectinload(MealNutritionSummaryModel.nutrients))
            .filter(
                MealNutritionSummaryModel.user_id == UUID(user_id.value),
                MealNutritionSummaryModel.date == target_date,
                MealNutritionSummaryModel.meal_type == meal_type.value,
                MealNutritionSummaryModel.meal_index == meal_index,
            )
            .one_or_none()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def list_by_user_and_date(
        self,
        *,
        user_id: UserId,
        target_date: date,
    ) -> Sequence[MealNutritionSummary]:
        models: Sequence[MealNutritionSummaryModel] = (
            self._session.query(MealNutritionSummaryModel)
            .options(selectinload(MealNutritionSummaryModel.nutrients))
            .filter(
                MealNutritionSummaryModel.user_id == UUID(user_id.value),
                MealNutritionSummaryModel.date == target_date,
            )
            .order_by(
                MealNutritionSummaryModel.meal_type.asc(),
                MealNutritionSummaryModel.meal_index.asc().nulls_last(),
            )
            .all()
        )
        return [self._to_entity(m) for m in models]

    def save(self, summary: MealNutritionSummary) -> None:
        """
        summary.id をキーに insert/update を行う。

        - 既存レコードがあれば更新
        - なければ新規作成
        """
        model = (
            self._session.query(MealNutritionSummaryModel)
            .options(selectinload(MealNutritionSummaryModel.nutrients))
            .filter(MealNutritionSummaryModel.id == summary.id.value)
            .one_or_none()
        )

        if model is None:
            model = MealNutritionSummaryModel(
                id=summary.id.value,
                user_id=UUID(summary.user_id.value),
                date=summary.date,
                meal_type=summary.meal_type.value,
                meal_index=summary.meal_index,
                generated_at=summary.generated_at,
                updated_at=summary.generated_at,
                nutrients=[],
            )
            self._apply_entity_to_model(summary, model)
            self._session.add(model)
        else:
            self._apply_entity_to_model(summary, model)
            # updated_at は DB 側の onupdate に任せる
