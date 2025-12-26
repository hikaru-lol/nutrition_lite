from __future__ import annotations

from app.application.profile.dto.profile_dto import ProfileDTO

from app.application.profile.ports.uow_port import ProfileUnitOfWorkPort

from app.domain.auth.value_objects import UserId
from app.domain.profile.errors import ProfileNotFoundError


class GetMyProfileUseCase:
    """
    現在ユーザーのプロフィールを取得するユースケース。

    - プロフィールが存在しない場合は UserNotFoundError を投げる。
      （将来的に ProfileNotFoundError を追加してもよい）
    """

    def __init__(self, uow: ProfileUnitOfWorkPort) -> None:
        self._uow = uow

    def execute(self, user_id: str) -> ProfileDTO:
        user_id = UserId(user_id)

        with self._uow as uow:
            profile = uow.profile_repo.get_by_user_id(user_id)
            if profile is None:
                raise ProfileNotFoundError("Profile not found.")

        return ProfileDTO(
            user_id=profile.user_id.value,
            sex=profile.sex,
            birthdate=profile.birthdate,
            height_cm=profile.height_cm.value,
            weight_kg=profile.weight_kg.value,
            image_id=profile.image_id.value if profile.image_id else None,
            meals_per_day=profile.meals_per_day,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
