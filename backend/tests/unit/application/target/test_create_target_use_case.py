from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.target.dto.target_dto import CreateTargetInputDTO
from app.application.target.use_cases.create_target import (
    CreateTargetUseCase,
    MAX_TARGETS_PER_USER,
)
from app.domain.auth.value_objects import UserId
from app.domain.target.value_objects import GoalType, ActivityLevel, NutrientCode
from app.application.target.errors import TargetLimitExceededError

from tests.unit.application.target.fakes import (
    FakeTargetRepository,
    FakeTargetSnapshotRepository,
    FakeTargetUnitOfWork,
    FakeTargetGenerator,
    make_target,
)


def test_create_target_first_becomes_active():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()
    uow = FakeTargetUnitOfWork(repo, snap_repo)
    generator = FakeTargetGenerator()
    use_case = CreateTargetUseCase(uow, generator)

    input_dto = CreateTargetInputDTO(
        user_id=user_id,
        title="First Target",
        goal_type=GoalType.WEIGHT_LOSS.value,
        goal_description=None,
        activity_level=ActivityLevel.LOW.value,
    )

    result = use_case.execute(input_dto)

    assert result.is_active is True
    targets = repo.list_by_user(UserId(user_id))
    assert len(targets) == 1
    assert targets[0].is_active is True
    assert len(result.nutrients) == len(list(NutrientCode))


def test_create_target_additional_is_not_active():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()

    existing = make_target(user_id, is_active=True)
    repo.add(existing)

    uow = FakeTargetUnitOfWork(repo, snap_repo)
    generator = FakeTargetGenerator()
    use_case = CreateTargetUseCase(uow, generator)

    input_dto = CreateTargetInputDTO(
        user_id=user_id,
        title="Second Target",
        goal_type=GoalType.MAINTAIN.value,
        goal_description=None,
        activity_level=ActivityLevel.NORMAL.value,
    )

    result = use_case.execute(input_dto)

    targets = repo.list_by_user(UserId(user_id))
    assert len(targets) == 2
    active_targets = [t for t in targets if t.is_active]
    assert result.is_active is False
    assert len(active_targets) == 1


def test_create_target_limit_exceeded():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()

    for i in range(MAX_TARGETS_PER_USER):
        t = make_target(user_id, title=f"T{i}")
        repo.add(t)

    uow = FakeTargetUnitOfWork(repo, snap_repo)
    generator = FakeTargetGenerator()
    use_case = CreateTargetUseCase(uow, generator)

    input_dto = CreateTargetInputDTO(
        user_id=user_id,
        title="Overflow Target",
        goal_type=GoalType.MAINTAIN.value,
        goal_description=None,
        activity_level=ActivityLevel.NORMAL.value,
    )

    with pytest.raises(TargetLimitExceededError):
        use_case.execute(input_dto)
