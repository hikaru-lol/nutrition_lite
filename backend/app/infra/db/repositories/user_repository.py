from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.domain.auth.entities import User
from app.domain.auth.value_objects import (
    EmailAddress,
    HashedPassword,
    TrialInfo,
    UserId,
    UserPlan,
)
from app.infra.db.models.user import UserModel


class SqlAlchemyUserRepository(UserRepositoryPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=UserId(model.id),
            email=EmailAddress(model.email),
            hashed_password=HashedPassword(model.hashed_password),
            name=model.name,
            plan=UserPlan(model.plan),
            trial_info=TrialInfo(trial_ends_at=model.trial_ends_at),
            has_profile=model.has_profile,
            created_at=model.created_at,
            deleted_at=model.deleted_at,
        )

    def _apply_entity_to_model(self, entity: User, model: Optional[UserModel] = None) -> UserModel:
        if model is None:
            model = UserModel(
                id=entity.id.value,
                email=entity.email.value,
                hashed_password=entity.hashed_password.value,
                name=entity.name,
                plan=entity.plan.value,
                trial_ends_at=entity.trial_info.trial_ends_at,
                has_profile=entity.has_profile,
                created_at=entity.created_at,
                deleted_at=entity.deleted_at,
            )
        else:
            model.email = entity.email.value
            model.hashed_password = entity.hashed_password.value
            model.name = entity.name
            model.plan = entity.plan.value
            model.trial_ends_at = entity.trial_info.trial_ends_at
            model.has_profile = entity.has_profile
            model.created_at = entity.created_at
            model.deleted_at = entity.deleted_at
        return model

    def get_by_id(self, user_id: UserId) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id.value)
        model = self._session.scalar(stmt)
        return self._to_entity(model) if model else None

    def get_by_email(self, email: EmailAddress) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email.value)
        model = self._session.scalar(stmt)
        return self._to_entity(model) if model else None

    def save(self, user: User) -> User:
        existing = self._session.get(UserModel, user.id.value)
        model = self._apply_entity_to_model(user, existing)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)
