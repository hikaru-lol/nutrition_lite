from __future__ import annotations

from uuid import UUID

from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.api.http.schemas.auth import UserSummary


def to_user_summary(dto: AuthUserDTO) -> UserSummary:
    user_id: UUID | str = getattr(dto, "id", None)

    plan_value = getattr(dto.plan, "value", dto.plan)

    return UserSummary(
        id=user_id,
        email=dto.email,
        name=dto.name,
        plan=plan_value,
        trial_ends_at=dto.trial_ends_at,
        has_profile=dto.has_profile,
        created_at=dto.created_at,
    )
