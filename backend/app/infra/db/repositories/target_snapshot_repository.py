from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.application.target.ports.target_snapshot_repository_port import (
    TargetSnapshotRepositoryPort,
)
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
    DailyTargetSnapshot 用の SQLAlchemy リポジトリ。
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Entity <-> Model
    # ------------------------------------------------------------------

    def _to_entity(self, model: DailyTargetSnapshotModel) -> DailyTargetSnapshot:
        nutrients = tuple(
            TargetNutrient(
                code=NutrientCode(n.code),
                amount=NutrientAmount(
                    value=n.amount_value,
                    unit=n.amount_unit,
                ),
                source=NutrientSource(n.source),
            )
            for n in model.nutrients
        )

        return DailyTargetSnapshot(
            user_id=UserId(str(model.user_id)),
            date=model.date,
            target_id=TargetId(str(model.target_id)),
            nutrients=nutrients,
            created_at=model.created_at,
        )

    def _from_entity(self, snapshot: DailyTargetSnapshot) -> DailyTargetSnapshotModel:
        model = DailyTargetSnapshotModel(
            user_id=UUID(snapshot.user_id.value),
            date=snapshot.date,
            target_id=UUID(snapshot.target_id.value),
            created_at=snapshot.created_at,
        )

        for n in snapshot.nutrients:
            model.nutrients.append(
                DailyTargetSnapshotNutrientModel(
                    code=n.code.value,
                    amount_value=n.amount.value,
                    amount_unit=n.amount.unit,
                    source=n.source.value,
                )
            )

        return model

    # ------------------------------------------------------------------
    # Port 実装
    # ------------------------------------------------------------------

    def add(self, snapshot: DailyTargetSnapshot) -> None:
        model = self._from_entity(snapshot)
        self._session.add(model)

    def get_by_user_and_date(
        self,
        user_id: UserId,
        snapshot_date: date,
    ) -> DailyTargetSnapshot | None:
        stmt = (
            select(DailyTargetSnapshotModel)
            .options(selectinload(DailyTargetSnapshotModel.nutrients))
            .where(
                DailyTargetSnapshotModel.user_id == UUID(user_id.value),
                DailyTargetSnapshotModel.date == snapshot_date,
            )
        )
        model = self._session.execute(stmt).scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    def list_by_user(
        self,
        user_id: UserId,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DailyTargetSnapshot]:
        stmt = (
            select(DailyTargetSnapshotModel)
            .options(selectinload(DailyTargetSnapshotModel.nutrients))
            .where(DailyTargetSnapshotModel.user_id == UUID(user_id.value))
            .order_by(DailyTargetSnapshotModel.date.asc())
        )
        if start_date is not None:
            stmt = stmt.where(DailyTargetSnapshotModel.date >= start_date)
        if end_date is not None:
            stmt = stmt.where(DailyTargetSnapshotModel.date <= end_date)

        models = self._session.execute(stmt).scalars().all()
        return [self._to_entity(m) for m in models]
