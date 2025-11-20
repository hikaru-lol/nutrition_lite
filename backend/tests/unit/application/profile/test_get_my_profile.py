from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from app.application.profile.use_cases.get_my_profile import GetMyProfileUseCase
from app.domain.auth.value_objects import UserId
from app.domain.profile.entities import Profile
from app.domain.profile.value_objects import Sex, HeightCm, WeightKg
from app.domain.auth.errors import UserNotFoundError
from tests.fakes.profile_repositories import InMemoryProfileRepository
from tests.fakes.profile_uow import FakeProfileUnitOfWork


def _make_use_case(repo: InMemoryProfileRepository) -> GetMyProfileUseCase:
    uow = FakeProfileUnitOfWork(profile_repo=repo)
    return GetMyProfileUseCase(uow=uow)


def test_get_my_profile_returns_existing_profile() -> None:
    repo = InMemoryProfileRepository()
    use_case = _make_use_case(repo)

    user_id = UserId("44444444-4444-4444-4444-444444444444")
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)

    profile = Profile(
        user_id=user_id,
        sex=Sex.MALE,
        birthdate=date(1995, 4, 1),
        height_cm=HeightCm(180.0),
        weight_kg=WeightKg(75.0),
        image_id=None,
        created_at=now,
        updated_at=now,
    )
    repo.save(profile)

    result = use_case.execute(user_id.value)

    assert result.user_id == user_id.value
    assert result.sex == profile.sex
    assert result.birthdate == profile.birthdate
    assert result.height_cm == profile.height_cm.value
    assert result.weight_kg == profile.weight_kg.value
    assert result.image_id is None
    assert result.created_at == profile.created_at
    assert result.updated_at == profile.updated_at


def test_get_my_profile_raises_when_not_found() -> None:
    repo = InMemoryProfileRepository()
    use_case = _make_use_case(repo)

    with pytest.raises(UserNotFoundError):
        use_case.execute("55555555-5555-5555-5555-555555555555")
