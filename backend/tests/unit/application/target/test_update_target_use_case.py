from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.target.dto.target_dto import (
    UpdateTargetInputDTO,
    UpdateTargetNutrientDTO,
)
from app.application.target.use_cases.update_target import UpdateTargetUseCase
from app.application.target.errors import TargetNotFoundError
from app.domain.target.value_objects import (
    GoalType,
    ActivityLevel,
    NutrientCode,
)
from app.domain.target.errors import InvalidTargetNutrientError

from tests.unit.application.target.fakes import (
    FakeTargetRepository,
    FakeTargetSnapshotRepository,
    FakeTargetUnitOfWork,
    make_target,
)


def test_update_target_updates_basic_fields_and_nutrients():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()

    target = make_target(user_id, title="Before",
                         goal_type=GoalType.WEIGHT_LOSS)
    repo.add(target)

    uow = FakeTargetUnitOfWork(repo, snap_repo)
    use_case = UpdateTargetUseCase(uow)

    patch_nutrients = [
        UpdateTargetNutrientDTO(
            code=NutrientCode.PROTEIN.value,
            amount=200.0,
            unit="g",
        )
    ]

    input_dto = UpdateTargetInputDTO(
        user_id=user_id,
        target_id=target.id.value,
        title="After",
        goal_type=GoalType.MAINTAIN.value,
        goal_description="Maintaining",
        activity_level=ActivityLevel.HIGH.value,
        llm_rationale="updated rationale",
        disclaimer="updated disclaimer",
        nutrients=patch_nutrients,
    )

    result = use_case.execute(input_dto)

    assert result.title == "After"
    assert result.goal_type == GoalType.MAINTAIN.value
    assert result.activity_level == ActivityLevel.HIGH.value
    assert result.llm_rationale == "updated rationale"

    stored = repo.get_by_id(target.user_id, target.id)
    assert stored is not None
    protein = stored.get_nutrient(NutrientCode.PROTEIN)
    assert protein is not None
    assert protein.amount.value == 200.0
    assert protein.amount.unit == "g"
    assert protein.source.value == "manual"


def test_update_target_invalid_nutrient_code_raises():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()

    target = make_target(user_id)
    repo.add(target)

    uow = FakeTargetUnitOfWork(repo, snap_repo)
    use_case = UpdateTargetUseCase(uow)

    patch_nutrients = [
        UpdateTargetNutrientDTO(
            code="unknown_nutrient",
            amount=100.0,
            unit="g",
        )
    ]

    input_dto = UpdateTargetInputDTO(
        user_id=user_id,
        target_id=target.id.value,
        nutrients=patch_nutrients,
    )

    with pytest.raises(InvalidTargetNutrientError):
        use_case.execute(input_dto)


def test_update_target_not_found():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()
    uow = FakeTargetUnitOfWork(repo, snap_repo)
    use_case = UpdateTargetUseCase(uow)

    input_dto = UpdateTargetInputDTO(
        user_id=user_id,
        target_id=str(uuid4()),
        title="Whatever",
    )

    with pytest.raises(TargetNotFoundError):
        use_case.execute(input_dto)
