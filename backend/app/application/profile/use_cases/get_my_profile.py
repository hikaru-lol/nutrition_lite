from __future__ import annotations

from app.application.profile.dto.profile_dto import ProfileDTO
from app.application.profile.ports.uow_port import ProfileUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.auth.errors import UserNotFoundError  # 暫定的に流用


class GetMyProfileUseCase:
    """
    現在ユーザーのプロフィールを取得するユースケース。

    - プロフィールが存在しない場合は UserNotFoundError を投げる。
      （将来的に ProfileNotFoundError を追加してもよい）
    """

    def __init__(self, uow: ProfileUnitOfWorkPort) -> None:
        self._uow = uow

    def execute(self, user_id: str) -> ProfileDTO:
        user_id_vo = UserId(user_id)

        with self._uow as uow:
            profile = uow.profile_repo.get_by_user_id(user_id_vo)
            if profile is None:
                # TODO: 必要であれば profile 用の専用エラーにする
                raise UserNotFoundError("Profile not found.")

        return ProfileDTO(
            user_id=profile.user_id.value,
            sex=profile.sex,
            birthdate=profile.birthdate,
            height_cm=profile.height_cm.value,
            weight_kg=profile.weight_kg.value,
            image_id=profile.image_id.value if profile.image_id else None,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
