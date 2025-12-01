from __future__ import annotations

from typing import List
from uuid import UUID

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, update

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

    # ------------------------------------------------------------------
    # Entity <-> Model 変換
    # ------------------------------------------------------------------

    def _to_entity(self, model: TargetModel) -> TargetDefinition:
        nutrients = [
            TargetNutrient(
                code=NutrientCode(n.code),
                amount=NutrientAmount(
                    value=n.amount_value,
                    unit=n.amount_unit,
                ),
                source=NutrientSource(n.source),
            )
            for n in model.nutrients
        ]

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

    def _apply_entity_to_model(
        self,
        entity: TargetDefinition,
        model: TargetModel,
    ) -> None:
        """
        Domain エンティティの状態を既存の TargetModel に反映する。

        - nutrients は一旦全削除してから再作成（シンプルな実装）
        """

        model.title = entity.title
        model.goal_type = entity.goal_type.value
        model.goal_description = entity.goal_description
        model.activity_level = entity.activity_level.value
        model.is_active = entity.is_active
        model.llm_rationale = entity.llm_rationale
        model.disclaimer = entity.disclaimer
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at

        # nutrients を入れ替え
        model.nutrients.clear()
        for n in entity.nutrients:
            model.nutrients.append(
                TargetNutrientModel(
                    target_id=model.id,
                    code=n.code.value,
                    amount_value=n.amount.value,
                    amount_unit=n.amount.unit,
                    source=n.source.value,
                )
            )

    # ------------------------------------------------------------------
    # Port 実装
    # ------------------------------------------------------------------

    def add(self, target: TargetDefinition) -> None:
        model = TargetModel(
            id=UUID(target.id.value),
            user_id=UUID(target.user_id.value),
            title=target.title,
            goal_type=target.goal_type.value,
            goal_description=target.goal_description,
            activity_level=target.activity_level.value,
            is_active=target.is_active,
            llm_rationale=target.llm_rationale,
            disclaimer=target.disclaimer,
            created_at=target.created_at,
            updated_at=target.updated_at,
        )

        # nutrients も一緒に追加
        for n in target.nutrients:
            model.nutrients.append(
                TargetNutrientModel(
                    code=n.code.value,
                    amount_value=n.amount.value,
                    amount_unit=n.amount.unit,
                    source=n.source.value,
                )
            )

        self._session.add(model)

    def get_by_id(
        self,
        user_id: UserId,
        target_id: TargetId,
    ) -> TargetDefinition | None:
        stmt = (
            select(TargetModel)
            .options(selectinload(TargetModel.nutrients))
            .where(
                TargetModel.id == UUID(target_id.value),
                TargetModel.user_id == UUID(user_id.value),
            )
        )
        result = self._session.execute(stmt).scalar_one_or_none()
        if result is None:
            return None
        return self._to_entity(result)

    def get_active(self, user_id: UserId) -> TargetDefinition | None:
        stmt = (
            select(TargetModel)
            .options(selectinload(TargetModel.nutrients))
            .where(
                TargetModel.user_id == UUID(user_id.value),
                TargetModel.is_active.is_(True),
            )
        )
        result = self._session.execute(stmt).scalar_one_or_none()
        if result is None:
            return None
        return self._to_entity(result)

    def list_by_user(
        self,
        user_id: UserId,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[TargetDefinition]:
        stmt = (
            select(TargetModel)
            .options(selectinload(TargetModel.nutrients))
            .where(TargetModel.user_id == UUID(user_id.value))
            .order_by(TargetModel.created_at.desc())
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)

        result = self._session.execute(stmt).scalars().all()
        return [self._to_entity(m) for m in result]

    def save(self, target: TargetDefinition) -> None:
        """
        既存 TargetDefinition の状態を DB に保存する。

        - Entity 側と Model 側を分離しているので、
          ここでは再度 Model を読み出してから状態を反映している。
        """
        stmt = (
            select(TargetModel)
            .options(selectinload(TargetModel.nutrients))
            .where(TargetModel.id == UUID(target.id.value))
        )
        model = self._session.execute(stmt).scalar_one_or_none()
        if model is None:
            # add() すべきケースかもしれないが、ここでは単純に何もしない
            return

        self._apply_entity_to_model(target, model)

    def deactivate_all(self, user_id: UserId) -> None:
        """
        指定ユーザーの TargetDefinition の is_active を全て False にする。
        """
        stmt = (
            update(TargetModel)
            .where(TargetModel.user_id == UUID(user_id.value))
            .values(is_active=False)
        )
        self._session.execute(stmt)
