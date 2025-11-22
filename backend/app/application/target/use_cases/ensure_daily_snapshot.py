from __future__ import annotations

from copy import deepcopy
from datetime import date

from app.application.auth.ports.clock_port import ClockPort
from app.application.target.ports.uow_port import TargetUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.target.entities import DailyTargetSnapshot, TargetNutrient
from app.domain.target import errors as target_errors


class EnsureDailySnapshotUseCase:
    """
    特定日に対して DailyTargetSnapshot を確定させるユースケース。

    ルール:
    - target_date が「今日以降」の場合は何もしない（スナップショットは過去日だけ）。
    - すでにスナップショットが存在する場合は何もしない（idempotent）。
    - スナップショットが無い過去日については、その日時点の active target をコピーして固定する。
    - active target が存在しなければ何もしない（または NoActiveTargetError を投げるのも選択肢）。
    """

    def __init__(self, uow: TargetUnitOfWorkPort, clock: ClockPort) -> None:
        self._uow = uow
        self._clock = clock

    def execute(self, user_id: str, target_date: date) -> None:
        today = self._clock.now().date()
        if target_date >= today:
            # 今日以降はスナップショットを作らないポリシー
            return

        user_id_vo = UserId(user_id)

        with self._uow as uow:
            existing = uow.snapshot_repo.get_by_user_and_date(
                user_id_vo, target_date)
            if existing is not None:
                # すでにスナップショットがある場合は何もしない（idempotent）
                return

            active = uow.target_repo.get_active_for_user(user_id_vo)
            if active is None:
                # アクティブなターゲットが無い場合の扱い：
                # - 何も作らない（以後の処理が snapshot の有無を考慮する前提）
                # - もしくは target_errors.NoActiveTargetError を投げる設計もあり。
                return

            # active の nutrients をコピーして snapshot を作成
            snapshot_nutrients = [
                TargetNutrient(
                    code=n.code,
                    amount=deepcopy(n.amount),
                    source=n.source,
                )
                for n in active.nutrients
            ]

            snapshot = DailyTargetSnapshot(
                user_id=user_id_vo,
                date=target_date,
                target_id=active.id,
                nutrients=snapshot_nutrients,
                created_at=self._clock.now(),
            )

            uow.snapshot_repo.save(snapshot)
            # commit は UoW の __exit__ で行われる
