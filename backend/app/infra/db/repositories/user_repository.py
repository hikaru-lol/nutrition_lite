from __future__ import annotations

from sqlalchemy.orm import Session

from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.domain.auth.entities import User
from app.domain.auth.value_objects import EmailAddress, UserId
from app.domain.auth.value_objects import UserPlan, TrialInfo  # など
from app.infra.db.models.user import UserModel


class SqlAlchemyUserRepository(UserRepositoryPort):
    def __init__(self, session: Session) -> None:
        self._session = session

    # --- Entity <-> Model の変換 ---------------------------------

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=UserId(str(model.id)),
            email=EmailAddress(model.email),
            hashed_password=model.hashed_password,  # HashedPassword(...) ならラップ
            name=model.name,
            plan=UserPlan(model.plan),
            trial_info=TrialInfo(trial_ends_at=model.trial_ends_at),
            has_profile=model.has_profile,
            created_at=model.created_at,
            deleted_at=model.deleted_at,
        )

    def _from_entity(self, entity: User) -> UserModel:
        existing: UserModel | None = self._session.get(
            UserModel, entity.id.value)
        if existing is None:
            model = UserModel(id=entity.id.value)
        else:
            model = existing

        model.email = entity.email.value
        model.hashed_password = entity.hashed_password.value
        model.name = entity.name
        model.plan = entity.plan.value
        model.trial_ends_at = entity.trial_info.trial_ends_at
        model.has_profile = entity.has_profile
        model.created_at = entity.created_at
        model.deleted_at = entity.deleted_at

        return model

    # --- Port 実装 -----------------------------------------------

    def get_by_id(self, user_id: UserId) -> User | None:
        model = (
            self._session.query(UserModel)
            .filter(
                UserModel.id == user_id.value,
                UserModel.deleted_at.is_(None),
            )
            .one_or_none()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def get_by_email(self, email: EmailAddress) -> User | None:
        model = (
            self._session.query(UserModel)
            .filter(
                UserModel.email == email.value,
                UserModel.deleted_at.is_(None),
            )
            .one_or_none()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def save(self, user: User) -> User:
        model = self._from_entity(user)
        self._session.add(model)
        return self._to_entity(model)
