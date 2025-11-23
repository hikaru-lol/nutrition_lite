from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest

from app.application.target.use_cases.ensure_daily_snapshot import (
    EnsureDailySnapshotUseCase,
    EnsureDailySnapshotInputDTO,
)
from app.application.target.errors import TargetNotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.target.entities import DailyTargetSnapshot

from .fakes import (
    FakeTargetRepository,
    FakeTargetSnapshotRepository,
    FakeTargetUnitOfWork,
    make_target,
)


def test_ensure_daily_snapshot_returns_existing_if_present():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()
    uow = FakeTargetUnitOfWork(repo, snap_repo)

    target = make_target(user_id, is_active=True)
    repo.add(target)

    snapshot_date = date(2024, 1, 1)
    existing_snapshot = DailyTargetSnapshot.from_target(
        target=target,
        snapshot_date=snapshot_date,
    )
    snap_repo.add(existing_snapshot)

    use_case = EnsureDailySnapshotUseCase(uow)

    input_dto = EnsureDailySnapshotInputDTO(
        user_id=user_id,
        target_date=snapshot_date,
    )

    result = use_case.execute(input_dto)

    assert result is existing_snapshot
    assert uow.committed is False


def test_ensure_daily_snapshot_creates_new_if_not_exists():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()
    uow = FakeTargetUnitOfWork(repo, snap_repo)

    target = make_target(user_id, is_active=True)
    repo.add(target)

    snapshot_date = date(2024, 1, 2)

    use_case = EnsureDailySnapshotUseCase(uow)

    input_dto = EnsureDailySnapshotInputDTO(
        user_id=user_id,
        target_date=snapshot_date,
    )

    result = use_case.execute(input_dto)

    assert result.user_id == target.user_id
    assert result.date == snapshot_date
    assert result.target_id == target.id
    assert len(result.nutrients) == len(target.nutrients)
    assert uow.committed is True

    stored = snap_repo.get_by_user_and_date(UserId(user_id), snapshot_date)
    assert stored is not None


def test_ensure_daily_snapshot_raises_if_no_active_target():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()
    uow = FakeTargetUnitOfWork(repo, snap_repo)

    use_case = EnsureDailySnapshotUseCase(uow)

    input_dto = EnsureDailySnapshotInputDTO(
        user_id=user_id,
        target_date=date(2024, 1, 3),
    )

    with pytest.raises(TargetNotFoundError):
        use_case.execute(input_dto)
