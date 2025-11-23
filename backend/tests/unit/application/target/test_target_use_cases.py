from __future__ import annotations

from datetime import datetime, date, timezone
from uuid import uuid4

import pytest

from app.application.target.dto.target_dto import (
    CreateTargetInputDTO,
    ListTargetsInputDTO,
    GetTargetInputDTO,
    GetActiveTargetInputDTO,
    UpdateTargetInputDTO,
    UpdateTargetNutrientDTO,
    ActivateTargetInputDTO,
)
from app.application.target.use_cases.create_target import (
    CreateTargetUseCase,
    MAX_TARGETS_PER_USER,
)
from app.application.target.use_cases.list_targets import ListTargetsUseCase
from app.application.target.use_cases.get_target import GetTargetUseCase
from app.application.target.use_cases.get_active_target import (
    GetActiveTargetUseCase,
)
from app.application.target.use_cases.update_target import UpdateTargetUseCase
from app.application.target.use_cases.activate_target import (
    ActivateTargetUseCase,
)
from app.application.target.use_cases.ensure_daily_snapshot import (
    EnsureDailySnapshotUseCase,
    EnsureDailySnapshotInputDTO,
)
from app.application.target.errors import TargetNotFoundError
from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.application.target.ports.target_generator_port import (
    TargetGeneratorPort,
    TargetGenerationContext,
    TargetGenerationResult,
)
from app.application.target.ports.target_repository_port import TargetRepositoryPort
from app.application.target.ports.target_snapshot_repository_port import (
    TargetSnapshotRepositoryPort,
)

from app.domain.auth.value_objects import UserId
from app.domain.target.entities import (
    TargetDefinition,
    TargetNutrient,
    DailyTargetSnapshot,
)
from app.domain.target.value_objects import (
    TargetId,
    GoalType,
    ActivityLevel,
    NutrientCode,
    NutrientAmount,
    NutrientSource,
)
from app.domain.target.errors import InvalidTargetNutrientError


# =====================================================================
# Fakes
# =====================================================================


class FakeTargetRepository(TargetRepositoryPort):
    """
    In-memory TargetRepositoryPort 実装（ユーザーごとに TargetDefinition を保持）。
    """

    def __init__(self) -> None:
        self._targets: list[TargetDefinition] = []

    # --- helper -------------------------------------------------------

    def _find_model(
        self,
        user_id: UserId,
        target_id: TargetId,
    ) -> TargetDefinition | None:
        for t in self._targets:
            if t.user_id == user_id and t.id == target_id:
                return t
        return None

    # --- Port 実装 ----------------------------------------------------

    def add(self, target: TargetDefinition) -> None:
        self._targets.append(target)

    def get_by_id(
        self,
        user_id: UserId,
        target_id: TargetId,
    ) -> TargetDefinition | None:
        return self._find_model(user_id, target_id)

    def get_active(self, user_id: UserId) -> TargetDefinition | None:
        for t in self._targets:
            if t.user_id == user_id and t.is_active:
                return t
        return None

    def list_by_user(
        self,
        user_id: UserId,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[TargetDefinition]:
        items = [t for t in self._targets if t.user_id == user_id]
        # created_at の新しい順
        items.sort(key=lambda t: t.created_at, reverse=True)
        if offset:
            items = items[offset:]
        if limit is not None:
            items = items[:limit]
        return list(items)

    def save(self, target: TargetDefinition) -> None:
        """
        in-memory なので何もする必要なし。
        TargetDefinition はミュータブルなので、参照のまま更新される。
        """
        # _find_model して差し替える実装でもOKだが、ここでは no-op
        return None

    def deactivate_all(self, user_id: UserId) -> None:
        for t in self._targets:
            if t.user_id == user_id:
                t.is_active = False


class FakeTargetSnapshotRepository(TargetSnapshotRepositoryPort):
    """
    In-memory DailyTargetSnapshot 用リポジトリ。
    """

    def __init__(self) -> None:
        self._snapshots: list[DailyTargetSnapshot] = []

    def add(self, snapshot: DailyTargetSnapshot) -> None:
        self._snapshots.append(snapshot)

    def get_by_user_and_date(
        self,
        user_id: UserId,
        snapshot_date: date,
    ) -> DailyTargetSnapshot | None:
        for s in self._snapshots:
            if s.user_id == user_id and s.date == snapshot_date:
                return s
        return None

    def list_by_user(
        self,
        user_id: UserId,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[DailyTargetSnapshot]:
        items = [s for s in self._snapshots if s.user_id == user_id]
        if start_date is not None:
            items = [s for s in items if s.date >= start_date]
        if end_date is not None:
            items = [s for s in items if s.date <= end_date]
        items.sort(key=lambda s: s.date)
        return list(items)


class FakeTargetUnitOfWork(TargetUnitOfWorkPort):
    """
    Target 用の in-memory UoW。

    - commit/rollback 呼び出し状況をテストから確認できるようにしている。
    """

    def __init__(
        self,
        target_repo: TargetRepositoryPort | None = None,
        target_snapshot_repo: TargetSnapshotRepositoryPort | None = None,
    ) -> None:
        self.target_repo = target_repo or FakeTargetRepository()
        self.target_snapshot_repo = target_snapshot_repo or FakeTargetSnapshotRepository()
        self.committed = False
        self._rollback_called = False

    def __enter__(self) -> "FakeTargetUnitOfWork":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self._rollback_called = True


class FakeTargetGenerator(TargetGeneratorPort):
    """
    TargetGeneratorPort の簡易 Fake。

    - すべての NutrientCode に対して固定値 100.0 + "g" を設定する。
      （実際の単位とはズレるが、テストとしては十分）
    """

    def generate(self, ctx: TargetGenerationContext) -> TargetGenerationResult:
        nutrients: list[TargetNutrient] = []
        for code in NutrientCode:
            nutrients.append(
                TargetNutrient(
                    code=code,
                    amount=NutrientAmount(value=100.0, unit="g"),
                    source=NutrientSource("llm"),
                )
            )
        return TargetGenerationResult(
            nutrients=nutrients,
            llm_rationale="fake rationale",
            disclaimer="fake disclaimer",
        )


# =====================================================================
# Helper: TargetDefinition 生成
# =====================================================================


def make_target(
    user_id: str,
    *,
    title: str = "My Target",
    goal_type: GoalType = GoalType.WEIGHT_LOSS,
    activity_level: ActivityLevel = ActivityLevel.NORMAL,
    is_active: bool = False,
    created_at: datetime | None = None,
) -> TargetDefinition:
    uid = UserId(user_id)
    tid = TargetId(str(uuid4()))
    if created_at is None:
        created_at = datetime.now(timezone.utc)

    nutrients = [
        TargetNutrient(
            code=code,
            amount=NutrientAmount(100.0, "g"),
            source=NutrientSource("llm"),
        )
        for code in NutrientCode
    ]

    return TargetDefinition(
        id=tid,
        user_id=uid,
        title=title,
        goal_type=goal_type,
        goal_description=None,
        activity_level=activity_level,
        nutrients=nutrients,
        is_active=is_active,
        created_at=created_at,
        updated_at=created_at,
        llm_rationale=None,
        disclaimer=None,
    )


# =====================================================================
# CreateTargetUseCase
# =====================================================================


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
    # 17 nutrients が入っていること
    assert len(result.nutrients) == len(list(NutrientCode))


def test_create_target_additional_is_not_active():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()

    # 既存 active ターゲットを 1 つ入れておく
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
    # 既存の active は一旦残っていて OK（Activate は別 UC の責務）
    active_targets = [t for t in targets if t.is_active]
    # 既に active がある状態なので、新規は active=False のはず
    assert result.is_active is False
    assert len(active_targets) == 1


def test_create_target_limit_exceeded():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()

    # 上限分のターゲットを事前に追加
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

    from app.domain.target.errors import TargetLimitExceededError

    with pytest.raises(TargetLimitExceededError):
        use_case.execute(input_dto)


# =====================================================================
# ListTargetsUseCase
# =====================================================================


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


# =====================================================================
# GetTargetUseCase
# =====================================================================


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


# =====================================================================
# GetActiveTargetUseCase
# =====================================================================


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


# =====================================================================
# ActivateTargetUseCase
# =====================================================================


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


# =====================================================================
# UpdateTargetUseCase
# =====================================================================


def test_update_target_updates_basic_fields_and_nutrients():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()

    target = make_target(user_id, title="Before",
                         goal_type=GoalType.WEIGHT_LOSS)
    repo.add(target)

    uow = FakeTargetUnitOfWork(repo, snap_repo)
    use_case = UpdateTargetUseCase(uow)

    # 例えば protein の量と unit を変更する
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

    # repository 上の entity も更新されていること
    stored = repo.get_by_id(UserId(user_id), target.id)
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

    # 存在しない code を指定
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


# =====================================================================
# EnsureDailySnapshotUseCase
# =====================================================================


def test_ensure_daily_snapshot_returns_existing_if_present():
    user_id = str(uuid4())
    repo = FakeTargetRepository()
    snap_repo = FakeTargetSnapshotRepository()
    uow = FakeTargetUnitOfWork(repo, snap_repo)

    target = make_target(user_id, is_active=True)
    repo.add(target)

    # 先に snapshot を追加しておく
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
    # 既存スナップショットを使う場合は commit しない実装なので、committed は False のまま
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

    # active target が存在しない状態
    use_case = EnsureDailySnapshotUseCase(uow)

    input_dto = EnsureDailySnapshotInputDTO(
        user_id=user_id,
        target_date=date(2024, 1, 3),
    )

    with pytest.raises(TargetNotFoundError):
        use_case.execute(input_dto)
