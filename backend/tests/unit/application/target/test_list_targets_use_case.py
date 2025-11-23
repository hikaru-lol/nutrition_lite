from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.application.target.dto.target_dto import ListTargetsInputDTO
from app.application.target.use_cases.list_targets import ListTargetsUseCase

from tests.unit.application.target.fakes import (
    FakeTargetRepository,
    FakeTargetSnapshotRepository,
    FakeTargetUnitOfWork,
    make_target,
)


def test_list_targets_returns_sorted_by_created_at_desc():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()

    older = make_target(
        user_id,
        title="old",
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    newer = make_target(
        user_id,
        title="new",
        created_at=datetime(2024, 2, 1, tzinfo=timezone.utc),
    )
    repo.add(older)
    repo.add(newer)

    uow = FakeTargetUnitOfWork(repo, snap_repo)
    use_case = ListTargetsUseCase(uow)

    input_dto = ListTargetsInputDTO(user_id=user_id, limit=None, offset=0)
    result = use_case.execute(input_dto)

    assert len(result) == 2
    assert result[0].title == "new"
    assert result[1].title == "old"
