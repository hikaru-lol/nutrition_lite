from __future__ import annotations

from datetime import datetime

from app.application.auth.ports.plan_checker_port import PlanCheckerPort
from app.application.auth.ports.uow_port import AuthUnitOfWorkPort
from app.application.auth.ports.clock_port import ClockPort
from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.domain.auth.errors import (
    UserNotFoundError,
    PremiumFeatureRequiredError,
)
from app.domain.auth.value_objects import UserId, UserPlan


class PlanCheckerService(PlanCheckerPort):
    """
    AuthUnitOfWork を使って User のプラン状態をチェックする実装。

    - trial_info.is_active(now) または plan == PAID ならプレミアム機能OK。
    - それ以外は PremiumFeatureRequiredError を投げる。
    """

    def __init__(
        self,
        auth_uow: AuthUnitOfWorkPort,
        clock: ClockPort,
    ) -> None:
        self._auth_uow = auth_uow
        self._clock = clock

    def ensure_premium_feature(self, user_id: UserId) -> None:
        now = self._clock.now()

        with self._auth_uow as uow:
            user_repo: UserRepositoryPort = uow.user_repo
            user = user_repo.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError(f"User not found: {user_id.value}")

            # trial 中なら許可
            if user.trial_info and user.trial_info.is_trial_active(now):
                return

            # trial 終了後は plan == PAID のみ許可
            if user.plan == UserPlan.PAID:
                return

            # それ以外は NG
            raise PremiumFeatureRequiredError(
                f"Premium feature requires trial or paid plan for user_id={user_id.value}"
            )
