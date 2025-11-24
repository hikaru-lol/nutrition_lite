from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.target.dto.target_dto import GetTargetInputDTO
from app.application.target.use_cases.get_target import GetTargetUseCase
from app.application.target.errors import TargetNotFoundError

from tests.unit.application.target.fakes import (
    FakeTargetRepository,
    FakeTargetSnapshotRepository,
    FakeTargetUnitOfWork,
    make_target,
)


def test_get_target_success():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()

    target = make_target(user_id, title="Target A")
    repo.add(target)

    uow = FakeTargetUnitOfWork(repo, snap_repo)
    use_case = GetTargetUseCase(uow)

    input_dto = GetTargetInputDTO(
        user_id=user_id,
        target_id=target.id.value,
    )

    result = use_case.execute(input_dto)

    assert result.id == target.id.value
    assert result.title == "Target A"


def test_get_target_not_found():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()
    uow = FakeTargetUnitOfWork(repo, snap_repo)
    use_case = GetTargetUseCase(uow)

    input_dto = GetTargetInputDTO(
        user_id=user_id,
        target_id=str(uuid4()),
    )

    with pytest.raises(TargetNotFoundError):
        use_case.execute(input_dto)
