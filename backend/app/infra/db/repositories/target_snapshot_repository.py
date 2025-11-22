from __future__ import annotations

from datetime import date
from typing import List

from sqlalchemy.orm import Session, joinedload

from app.application.target.ports.target_snapshot_repository_port import TargetSnapshotRepositoryPort
from app.domain.auth.value_objects import UserId
from app.domain.target.entities import DailyTargetSnapshot, TargetNutrient
from app.domain.target.value_objects import (
    TargetId,
    NutrientCode,
    NutrientAmount,
    NutrientSource,
)
from app.infra.db.models.target import (
    DailyTargetSnapshotModel,
    DailyTargetSnapshotNutrientModel,
)


class SqlAlchemyTargetSnapshotRepository(TargetSnapshotRepositoryPort):
    """
    TargetSnapshotRepositoryPort の SQLAlchemy 実装。
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # --- Entity <-> Model 変換 ---------------------------------------

    def _nutrient_model_to_entity(self, model: DailyTargetSnapshotNutrientModel) -> TargetNutrient:
        return TargetNutrient(
            code=NutrientCode(model.code),
            amount=NutrientAmount(value=model.amount, unit=model.unit),
            source=NutrientSource(model.source),
        )

    def _nutrient_entity_to_model(
        self,
        entity: TargetNutrient,
        snapshot_id: str,
    ) -> DailyTargetSnapshotNutrientModel:
        return DailyTargetSnapshotNutrientModel(
            snapshot_id=snapshot_id,
            code=entity.code.value,
            amount=entity.amount.value,
            unit=entity.amount.unit,
            source=entity.source.value,
        )

    def _to_entity(self, model: DailyTargetSnapshotModel) -> DailyTargetSnapshot:
        nutrients = [self._nutrient_model_to_entity(
            nm) for nm in model.nutrients]
        return DailyTargetSnapshot(
            user_id=UserId(str(model.user_id)),
            date=model.date,
            # type: ignore[arg-type]
            target_id=TargetId(str(model.target_id)
                               ) if model.target_id is not None else None,
            nutrients=nutrients,
            created_at=model.created_at,
        )

    def _from_entity(self, entity: DailyTargetSnapshot) -> DailyTargetSnapshotModel:
        # (user_id, date) はユニークなので、それで既存を検索する
        existing: DailyTargetSnapshotModel | None = (
            self._session.query(DailyTargetSnapshotModel)
            .filter(
                DailyTargetSnapshotModel.user_id == entity.user_id.value,
                DailyTargetSnapshotModel.date == entity.date,
            )
            .one_or_none()
        )
        if existing is None:
            model = DailyTargetSnapshotModel(
                user_id=entity.user_id.value,
                date=entity.date,
            )
        else:
            model = existing

        model.target_id = entity.target_id.value
        model.created_at = entity.created_at

        # nutrients を差し替え
        model.nutrients.clear()
        for n in entity.nutrients:
            model.nutrients.append(
                # id は新規時は None → flush 後に振られる
                self._nutrient_entity_to_model(n, model.id or None)
            )

        return model

    # --- Port 実装 ---------------------------------------------------

    def get_by_user_and_date(self, user_id: UserId, target_date: date) -> DailyTargetSnapshot | None:
        model: DailyTargetSnapshotModel | None = (
            self._session.query(DailyTargetSnapshotModel)
            .options(joinedload(DailyTargetSnapshotModel.nutrients))
            .filter(
                DailyTargetSnapshotModel.user_id == user_id.value,
                DailyTargetSnapshotModel.date == target_date,
            )
            .one_or_none()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def save(self, snapshot: DailyTargetSnapshot) -> DailyTargetSnapshot:
        model = self._from_entity(snapshot)
        self._session.add(model)
        self._session.flush()
        return self._to_entity(model)
