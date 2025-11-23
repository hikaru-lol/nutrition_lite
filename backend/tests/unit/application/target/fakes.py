from __future__ import annotations

from datetime import datetime, date, timezone
from uuid import uuid4

from app.application.target.ports.target_repository_port import TargetRepositoryPort
from app.application.target.ports.target_snapshot_repository_port import (
    TargetSnapshotRepositoryPort,
)
from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.application.target.ports.target_generator_port import (
    TargetGeneratorPort,
    TargetGenerationContext,
    TargetGenerationResult,
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


# =====================================================================
# Fake repositories / UoW / generator
# =====================================================================


class FakeTargetRepository(TargetRepositoryPort):
    """
    In-memory TargetRepositoryPort 実装。
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
        items.sort(key=lambda t: t.created_at, reverse=True)
        if offset:
            items = items[offset:]
        if limit is not None:
            items = items[:limit]
        return list(items)

    def save(self, target: TargetDefinition) -> None:
        # in-memory なので no-op で OK（ミュータブル Entity を直接更新している）
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

    - commit/rollback 呼び出しをテストから確認できる。
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

    - すべての NutrientCode に対して固定値 100.0 g を設定。
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
