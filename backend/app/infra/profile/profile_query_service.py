from __future__ import annotations

from app.application.profile.ports.profile_query_port import (
    ProfileQueryPort,
    ProfileForTarget,
    ProfileForDailyLog,
    ProfileForRecommendation,
)
from app.application.profile.use_cases.get_my_profile import GetMyProfileUseCase
from app.domain.auth.value_objects import UserId
from app.domain.profile.errors import ProfileNotFoundError as DomainProfileNotFoundError


class ProfileQueryService(ProfileQueryPort):
    """
    Profile の GetMyProfileUseCase をラップして、
    他コンテキスト向けの ProfileQueryPort を満たすアダプタ。
    """

    def __init__(self, get_my_profile_uc: GetMyProfileUseCase) -> None:
        self._get_my_profile_uc = get_my_profile_uc

    def _get_profile_output(self, user_id: UserId):
        """
        内部的に GetMyProfileUseCase を呼び出す共通ヘルパー。
        """
        try:
            return self._get_my_profile_uc.execute(user_id=user_id.value)
        except DomainProfileNotFoundError:
            return None

    # --- Target 用 -----------------------------------------------------

    def get_profile_for_target(self, user_id: UserId) -> ProfileForTarget | None:
        output = self._get_profile_output(user_id)
        if output is None:
            return None

        return ProfileForTarget(
            sex=(output.sex.value if getattr(
                output, "sex", None) is not None else None),
            birthdate=getattr(output, "birthdate", None),
            height_cm=getattr(output, "height_cm", None),
            weight_kg=getattr(output, "weight_kg", None),
        )

    # --- DailyLog 用 ---------------------------------------------------

    def get_profile_for_daily_log(self, user_id: UserId) -> ProfileForDailyLog | None:
        output = self._get_profile_output(user_id)
        if output is None:
            return None

        return ProfileForDailyLog(
            meals_per_day=getattr(output, "meals_per_day", None),
        )

# --- Recommendation 用 --------------------------------------------

    def get_profile_for_recommendation(
        self,
        user_id: UserId,
    ) -> ProfileForRecommendation | None:
        """
        MealRecommendation 用に、提案に使いたいプロフィール情報だけを返す。

        - sex / birthdate / height_cm / weight_kg / meals_per_day を含む。
        """
        output = self._get_profile_output(user_id)
        if output is None:
            return None

        return ProfileForRecommendation(
            sex=(output.sex.value if getattr(
                output, "sex", None) is not None else None),
            birthdate=getattr(output, "birthdate", None),
            height_cm=getattr(output, "height_cm", None),
            weight_kg=getattr(output, "weight_kg", None),
            meals_per_day=getattr(output, "meals_per_day", None),
        )
