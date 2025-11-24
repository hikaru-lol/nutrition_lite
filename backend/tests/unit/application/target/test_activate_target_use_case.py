from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.target.dto.target_dto import ActivateTargetInputDTO
from app.application.target.use_cases.activate_target import ActivateTargetUseCase
from app.application.target.errors import TargetNotFoundError
from app.domain.auth.value_objects import UserId

from tests.unit.application.target.fakes import (
    FakeTargetRepository,
    FakeTargetSnapshotRepository,
    FakeTargetUnitOfWork,
    make_target,
)


def test_activate_target_switches_active_flag_and_deactivates_others():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()

    t1 = make_target(user_id, title="T1", is_active=True)
    t2 = make_target(user_id, title="T2", is_active=False)
    repo.add(t1)
    repo.add(t2)

    uow = FakeTargetUnitOfWork(repo, snap_repo)
    use_case = ActivateTargetUseCase(uow)

    input_dto = ActivateTargetInputDTO(
        user_id=user_id,
        target_id=t2.id.value,
    )

    result = use_case.execute(input_dto)

    assert uow.committed is True

    targets = repo.list_by_user(UserId(user_id))
    active_targets = [t for t in targets if t.is_active]
    assert len(active_targets) == 1
    assert active_targets[0].id == t2.id

    assert result.id == t2.id.value
    assert result.is_active is True


def test_activate_target_not_found():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()
    uow = FakeTargetUnitOfWork(repo, snap_repo)
    use_case = ActivateTargetUseCase(uow)

    input_dto = ActivateTargetInputDTO(
        user_id=user_id,
        target_id=str(uuid4()),
    )

    with pytest.raises(TargetNotFoundError):
        use_case.execute(input_dto)
