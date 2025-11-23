from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.target.dto.target_dto import GetActiveTargetInputDTO
from app.application.target.use_cases.get_active_target import (
    GetActiveTargetUseCase,
)
from app.application.target.errors import TargetNotFoundError

from .fakes import (
    FakeTargetRepository,
    FakeTargetSnapshotRepository,
    FakeTargetUnitOfWork,
    make_target,
)


def test_get_active_target_success():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()

    t1 = make_target(user_id, title="Inactive", is_active=False)
    t2 = make_target(user_id, title="Active", is_active=True)
    repo.add(t1)
    repo.add(t2)

    uow = FakeTargetUnitOfWork(repo, snap_repo)
    use_case = GetActiveTargetUseCase(uow)

    input_dto = GetActiveTargetInputDTO(user_id=user_id)
    result = use_case.execute(input_dto)

    assert result.title == "Active"
    assert result.is_active is True


def test_get_active_target_not_found():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()
    uow = FakeTargetUnitOfWork(repo, snap_repo)
    use_case = GetActiveTargetUseCase(uow)

    input_dto = GetActiveTargetInputDTO(user_id=user_id)

    with pytest.raises(TargetNotFoundError):
        use_case.execute(input_dto)
