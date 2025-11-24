from __future__ import annotations

from datetime import date

from app.application.target.ports.profile_query_port import (
    ProfileQueryPort,
    ProfileForTarget,
)
from app.application.profile.use_cases.get_my_profile import GetMyProfileUseCase
from app.domain.auth.value_objects import UserId
from app.domain.profile.errors import ProfileNotFoundError as DomainProfileNotFoundError


class ProfileQueryService(ProfileQueryPort):
    """
    Profile の GetMyProfileUseCase をラップして、
    Target 側の ProfileQueryPort を満たすアダプタ。
    """

    def __init__(self, get_my_profile_uc: GetMyProfileUseCase) -> None:
        self._get_my_profile_uc = get_my_profile_uc

    def get_profile_for_target(self, user_id: UserId) -> ProfileForTarget | None:
        try:
            # GetMyProfileUseCase のインターフェイスに合わせて呼び出す
            # 例: output = self._get_my_profile_uc.execute(user_id=user_id.value)
            output = self._get_my_profile_uc.execute(user_id=user_id.value)
        except DomainProfileNotFoundError:
            return None

        # output がどんな DTO かは既存実装次第だが、
        # だいたい sex/birthdate/height_cm/weight_kg を持っているはずなのでそれを抜き出す。
        return ProfileForTarget(
            sex=(output.sex.value if getattr(
                output, "sex", None) is not None else None),
            birthdate=getattr(output, "birthdate", None),
            height_cm=getattr(output, "height_cm", None),
            weight_kg=getattr(output, "weight_kg", None),
        )
