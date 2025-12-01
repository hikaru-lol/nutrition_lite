from __future__ import annotations

from datetime import date
from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from app.application.nutrition.ports.daily_nutrition_repository_port import (
    DailyNutritionSummaryRepositoryPort,
)
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_nutrition import (
    DailyNutritionSummary,
    DailyNutritionSummaryId,
    DailyNutrientIntake,
)
from app.domain.target.value_objects import NutrientCode, NutrientAmount, NutrientSource
from app.infra.db.models.daily_nutrition import (
    DailyNutritionSummaryModel,
    DailyNutritionNutrientModel,
)


class SqlAlchemyDailyNutritionSummaryRepository(DailyNutritionSummaryRepositoryPort):
    """
    DailyNutritionSummaryRepositoryPort の SQLAlchemy 実装。
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # --- Entity <-> Model 変換 ----------------------------------------

    def _to_entity(self, model: DailyNutritionSummaryModel) -> DailyNutritionSummary:
        nutrients: list[DailyNutrientIntake] = []
        for n in model.nutrients:
            nutrients.append(
                DailyNutrientIntake(
                    code=NutrientCode(n.code),
                    amount=NutrientAmount(
                        value=n.amount_value, unit=n.amount_unit),
                    source=NutrientSource(n.source),
                )
            )

        return DailyNutritionSummary(
            id=DailyNutritionSummaryId(model.id),
            user_id=UserId(str(model.user_id)),
            date=model.date,
            nutrients=nutrients,
            generated_at=model.generated_at,
        )

    def _apply_entity_to_model(
        self,
        entity: DailyNutritionSummary,
        model: DailyNutritionSummaryModel,
    ) -> None:
        """
        Entity の内容を既存の Model に反映する（nutrients は入れ替え）。
        """
        model.user_id = UUID(entity.user_id.value)
        model.date = entity.date
        # generated_at は原則として初回作成時の値を維持したいので、ここでは触らない

        # nutrients: いったん全部消して入れ直すシンプルな実装
        model.nutrients.clear()
        for n in entity.nutrients:
            model.nutrients.append(
                DailyNutritionNutrientModel(
                    summary_id=model.id,
                    code=n.code.value,
                    amount_value=n.amount.value,
                    amount_unit=n.amount.unit,
                    source=n.source.value,
                )
            )

    # --- Port 実装 -----------------------------------------------------

    def get_by_user_and_date(
        self,
        *,
        user_id: UserId,
        target_date: date,
    ) -> DailyNutritionSummary | None:
        model = (
            self._session.query(DailyNutritionSummaryModel)
            .options(selectinload(DailyNutritionSummaryModel.nutrients))
            .filter(
                DailyNutritionSummaryModel.user_id == UUID(user_id.value),
                DailyNutritionSummaryModel.date == target_date,
            )
            .one_or_none()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def list_by_user_and_range(
        self,
        *,
        user_id: UserId,
        start_date: date,
        end_date: date,
    ) -> Sequence[DailyNutritionSummary]:
        models: Sequence[DailyNutritionSummaryModel] = (
            self._session.query(DailyNutritionSummaryModel)
            .options(selectinload(DailyNutritionSummaryModel.nutrients))
            .filter(
                DailyNutritionSummaryModel.user_id == UUID(user_id.value),
                DailyNutritionSummaryModel.date >= start_date,
                DailyNutritionSummaryModel.date <= end_date,
            )
            .order_by(DailyNutritionSummaryModel.date.asc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def save(self, summary: DailyNutritionSummary) -> None:
        """
        summary.id をキーに insert/update を行う。

        - 既存レコードがあれば更新
        - なければ新規作成
        """
        model = (
            self._session.query(DailyNutritionSummaryModel)
            .options(selectinload(DailyNutritionSummaryModel.nutrients))
            .filter(DailyNutritionSummaryModel.id == summary.id.value)
            .one_or_none()
        )

        if model is None:
            model = DailyNutritionSummaryModel(
                id=summary.id.value,
                user_id=UUID(summary.user_id.value),
                date=summary.date,
                generated_at=summary.generated_at,
                updated_at=summary.generated_at,
                nutrients=[],
            )
            self._apply_entity_to_model(summary, model)
            self._session.add(model)
        else:
            self._apply_entity_to_model(summary, model)
            # updated_at は DB側の onupdate に任せる
