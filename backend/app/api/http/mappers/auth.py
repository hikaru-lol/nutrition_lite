
from app.application.auth.dto import AuthUserDTO
from app.api.http.schemas.auth import UserSummary


def to_user_summary(dto: AuthUserDTO) -> UserSummary:
    return UserSummary(
        id=dto.id,
        email=dto.email,
        name=dto.name,
        plan=dto.plan.value if hasattr(dto.plan, "value") else dto.plan,
        trial_ends_at=dto.trial_ends_at,
        has_profile=dto.has_profile,
        created_at=dto.created_at,
    )
