from __future__ import annotations

from datetime import date
from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.nutrition.ports.daily_report_repository_port import (
    DailyNutritionReportRepositoryPort,
)
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_report import (
    DailyNutritionReport,
    DailyNutritionReportId,
)
from app.infra.db.models.daily_nutrition_report import DailyNutritionReportModel


class SqlAlchemyDailyNutritionReportRepository(DailyNutritionReportRepositoryPort):
    """
    DailyNutritionReportRepositoryPort の SQLAlchemy 実装。

    - DB 側の user_id は UUID
    - ドメイン側の UserId は UUID 文字列を包んだ VO
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # --- 内部ヘルパー -----------------------------------------------

    def _user_id_to_db(self, user_id: UserId) -> UUID:
        """
        ドメインの UserId (str) -> DB 用 UUID への変換。
        """
        return UUID(user_id.value)

    def _to_entity(self, model: DailyNutritionReportModel) -> DailyNutritionReport:
        return DailyNutritionReport(
            id=DailyNutritionReportId(model.id),
            # model.user_id は UUID → str にして詰める
            user_id=UserId(str(model.user_id)),
            date=model.date,
            summary=model.summary,
            good_points=list(model.good_points or []),
            improvement_points=list(model.improvement_points or []),
            tomorrow_focus=list(model.tomorrow_focus or []),
            created_at=model.created_at,
        )

    def _update_model_from_entity(
        self,
        model: DailyNutritionReportModel,
        entity: DailyNutritionReport,
    ) -> None:
        # entity.user_id.value は UUID 文字列想定
        model.user_id = UUID(entity.user_id.value)
        model.date = entity.date
        model.summary = entity.summary
        model.good_points = list(entity.good_points)
        model.improvement_points = list(entity.improvement_points)
        model.tomorrow_focus = list(entity.tomorrow_focus)
        model.created_at = entity.created_at

    # --- RepositoryPort 実装 ------------------------------------------

    def get_by_user_and_date(
        self,
        user_id: UserId,
        target_date: date,
    ) -> DailyNutritionReport | None:
        stmt = (
            select(DailyNutritionReportModel)
            .where(
                DailyNutritionReportModel.user_id == self._user_id_to_db(
                    user_id),
                DailyNutritionReportModel.date == target_date,
            )
        )
        model = self._session.scalar(stmt)
        if model is None:
            return None
        return self._to_entity(model)

    def list_recent(
        self,
        user_id: UserId,
        limit: int,
    ) -> Sequence[DailyNutritionReport]:
        stmt = (
            select(DailyNutritionReportModel)
            .where(
                DailyNutritionReportModel.user_id == self._user_id_to_db(
                    user_id),
            )
            .order_by(DailyNutritionReportModel.date.desc())
            .limit(limit)
        )
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    def save(self, report: DailyNutritionReport) -> None:
        """
        - id が既存テーブルに存在すれば update
        - なければ insert
        """
        model = self._session.get(DailyNutritionReportModel, report.id.value)
        if model is None:
            model = DailyNutritionReportModel(id=report.id.value)
            self._session.add(model)

        self._update_model_from_entity(model, report)
        # commit は Unit of Work / 外側に任せる
