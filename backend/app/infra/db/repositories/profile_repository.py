from __future__ import annotations

from sqlalchemy.orm import Session

from app.application.profile.ports.profile_repository_port import ProfileRepositoryPort
from app.domain.auth.value_objects import UserId
from app.domain.profile.entities import Profile
from app.domain.profile.value_objects import (
    Sex,
    HeightCm,
    WeightKg,
    ProfileImageId,
)
from app.infra.db.models.profile import ProfileModel


class SqlAlchemyProfileRepository(ProfileRepositoryPort):
    """
    ProfileRepositoryPort の SQLAlchemy 実装。
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # --- Entity <-> Model 変換 ---------------------------------------

    def _to_entity(self, model: ProfileModel) -> Profile:
        return Profile(
            user_id=UserId(str(model.user_id)),
            sex=Sex(model.sex),
            birthdate=model.birthdate,
            height_cm=HeightCm(model.height_cm),
            weight_kg=WeightKg(model.weight_kg),
            image_id=ProfileImageId(
                model.image_id) if model.image_id else None,
            meals_per_day=model.meals_per_day,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _from_entity(self, entity: Profile) -> ProfileModel:
        existing: ProfileModel | None = self._session.get(
            ProfileModel, entity.user_id.value)
        if existing is None:
            model = ProfileModel(user_id=entity.user_id.value)
        else:
            model = existing

        model.sex = entity.sex.value
        model.birthdate = entity.birthdate
        model.height_cm = entity.height_cm.value
        model.weight_kg = entity.weight_kg.value
        model.image_id = entity.image_id.value if entity.image_id else None
        model.meals_per_day = entity.meals_per_day
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at

        return model

    # --- Port 実装 ---------------------------------------------------

    def get_by_user_id(self, user_id: UserId) -> Profile | None:
        model = self._session.get(ProfileModel, user_id.value)
        if model is None:
            return None
        return self._to_entity(model)

    def save(self, profile: Profile) -> Profile:
        """
        新規 or 更新を同じメソッドで扱う。
        commit は UoW 側で行う前提なので、ここでは flush までにとどめる。
        """

        model = self._from_entity(profile)

        self._session.add(model)

        # auth と同様、必要なら flush() して PK や制約エラーを早めに検出してもよい
        self._session.flush()

        return self._to_entity(model)
