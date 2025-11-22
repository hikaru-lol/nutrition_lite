from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session, joinedload

from app.application.target.ports.target_repository_port import TargetRepositoryPort
from app.domain.auth.value_objects import UserId
from app.domain.target.entities import TargetDefinition, TargetNutrient
from app.domain.target.value_objects import (
    TargetId,
    GoalType,
    ActivityLevel,
    NutrientCode,
    NutrientAmount,
    NutrientSource,
)
from app.infra.db.models.target import TargetModel, TargetNutrientModel


class SqlAlchemyTargetRepository(TargetRepositoryPort):
    """
    TargetRepositoryPort の SQLAlchemy 実装。
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # --- Entity <-> Model 変換 ---------------------------------------

    def _nutrient_model_to_entity(self, model: TargetNutrientModel) -> TargetNutrient:
        return TargetNutrient(
            code=NutrientCode(model.code),
            amount=NutrientAmount(value=model.amount, unit=model.unit),
            source=NutrientSource(model.source),
        )

    def _nutrient_entity_to_model(
        self,
        entity: TargetNutrient,
        target_id: TargetId,
    ) -> TargetNutrientModel:
        return TargetNutrientModel(
            target_id=target_id.value,
            code=entity.code.value,
            amount=entity.amount.value,
            unit=entity.amount.unit,
            source=entity.source.value,
        )

    def _to_entity(self, model: TargetModel) -> TargetDefinition:
        nutrients = [self._nutrient_model_to_entity(
            nm) for nm in model.nutrients]
        return TargetDefinition(
            id=TargetId(str(model.id)),
            user_id=UserId(str(model.user_id)),
            title=model.title,
            goal_type=GoalType(model.goal_type),
            goal_description=model.goal_description,
            activity_level=ActivityLevel(model.activity_level),
            nutrients=nutrients,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            llm_rationale=model.llm_rationale,
            disclaimer=model.disclaimer,
        )

    def _from_entity(self, entity: TargetDefinition) -> TargetModel:
        existing: TargetModel | None = self._session.get(
            TargetModel, entity.id.value)
        if existing is None:
            model = TargetModel(id=entity.id.value)
        else:
            model = existing

        model.user_id = entity.user_id.value
        model.title = entity.title
        model.goal_type = entity.goal_type.value
        model.goal_description = entity.goal_description
        model.activity_level = entity.activity_level.value
        model.is_active = entity.is_active
        model.llm_rationale = entity.llm_rationale
        model.disclaimer = entity.disclaimer
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at

        # nutrients は一度全削除して差し替える
        model.nutrients.clear()
        for n in entity.nutrients:
            model.nutrients.append(
                self._nutrient_entity_to_model(n, entity.id)
            )

        return model

    # --- Port 実装 ---------------------------------------------------

    def list_for_user(self, user_id: UserId) -> List[TargetDefinition]:
        models: List[TargetModel] = (
            self._session.query(TargetModel)
            .options(joinedload(TargetModel.nutrients))
            .filter(TargetModel.user_id == user_id.value)
            .order_by(TargetModel.created_at.asc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def get_by_id(self, user_id: UserId, target_id: TargetId) -> TargetDefinition | None:
        model: TargetModel | None = (
            self._session.query(TargetModel)
            .options(joinedload(TargetModel.nutrients))
            .filter(
                TargetModel.user_id == user_id.value,
                TargetModel.id == target_id.value,
            )
            .one_or_none()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def get_active_for_user(self, user_id: UserId) -> TargetDefinition | None:
        model: TargetModel | None = (
            self._session.query(TargetModel)
            .options(joinedload(TargetModel.nutrients))
            .filter(
                TargetModel.user_id == user_id.value,
                TargetModel.is_active == True,  # noqa: E712
            )
            .one_or_none()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def count_for_user(self, user_id: UserId) -> int:
        return (
            self._session.query(TargetModel)
            .filter(TargetModel.user_id == user_id.value)
            .count()
        )

    def save(self, target: TargetDefinition) -> TargetDefinition:
        model = self._from_entity(target)
        self._session.add(model)
        # commit は UoW が行うので、ここでは flush まで
        self._session.flush()
        return self._to_entity(model)
