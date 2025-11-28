from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from app.application.profile.dto.profile_dto import ProfileDTO, UpsertProfileInputDTO
from app.application.profile.ports.uow_port import ProfileUnitOfWorkPort
from app.application.profile.ports.profile_image_storage_port import ProfileImageStoragePort
from app.domain.auth.value_objects import UserId
from app.domain.profile.entities import Profile
from app.domain.profile.value_objects import HeightCm, WeightKg, ProfileImageId


class UpsertProfileUseCase:
    """
    プロフィールの作成 / 更新を行うユースケース。

    - 基本情報（性別 / 生年月日 / 身長 / 体重）
    - プロフィール画像（任意）
    """

    def __init__(
        self,
        uow: ProfileUnitOfWorkPort,
        image_storage: ProfileImageStoragePort,
    ) -> None:
        self._uow = uow
        self._image_storage = image_storage

    def execute(self, input_dto: UpsertProfileInputDTO) -> ProfileDTO:
        now = datetime.now(timezone.utc)
        user_id = UserId(input_dto.user_id)

        with self._uow as uow:
            existing = uow.profile_repo.get_by_user_id(user_id)

            # 既存の image_id（あれば）を引き継ぐ
            image_id: Optional[ProfileImageId] = existing.image_id if existing else None

            # 画像が送られてきている場合は新しく保存する
            if input_dto.image_content is not None and input_dto.image_content_type is not None:
                stored = self._image_storage.save(
                    user_id=user_id,
                    content=input_dto.image_content,
                    content_type=input_dto.image_content_type,
                )
                image_id = stored.id

            if existing is None:
                profile = Profile(
                    user_id=user_id,
                    sex=input_dto.sex,
                    birthdate=input_dto.birthdate,
                    height_cm=HeightCm(input_dto.height_cm),
                    weight_kg=WeightKg(input_dto.weight_kg),
                    image_id=image_id,
                    meals_per_day=input_dto.meals_per_day,
                    created_at=now,
                    updated_at=now,
                )
            else:
                existing.sex = input_dto.sex
                existing.birthdate = input_dto.birthdate
                existing.height_cm = HeightCm(input_dto.height_cm)
                existing.weight_kg = WeightKg(input_dto.weight_kg)
                existing.image_id = image_id
                existing.meals_per_day = input_dto.meals_per_day
                existing.updated_at = now
                profile = existing

            saved = uow.profile_repo.save(profile)
            # commit / rollback は UoW の __exit__ に任せる

        return ProfileDTO(
            user_id=saved.user_id.value,
            sex=saved.sex,
            birthdate=saved.birthdate,
            height_cm=saved.height_cm.value,
            weight_kg=saved.weight_kg.value,
            image_id=saved.image_id.value if saved.image_id else None,
            meals_per_day=saved.meals_per_day,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )
