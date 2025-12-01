from __future__ import annotations

from datetime import date as DateType
from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import Session

from app.application.nutrition.ports.recommendation_repository_port import (
    MealRecommendationRepositoryPort,
)
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.meal_recommendation import (
    MealRecommendation,
    MealRecommendationId,
)
from app.infra.db.models.meal_recommendation import MealRecommendationModel


class SqlAlchemyMealRecommendationRepository(MealRecommendationRepositoryPort):
    """
    MealRecommendationRepositoryPort の SQLAlchemy 実装。
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Entity <-> Model 変換
    # ------------------------------------------------------------------

    def _to_entity(self, model: MealRecommendationModel) -> MealRecommendation:
        return MealRecommendation(
            id=MealRecommendationId(str(model.id)),
            user_id=UserId(str(model.user_id)),
            generated_for_date=model.generated_for_date,
            body=model.body,
            tips=list(model.tips or []),
            created_at=model.created_at,
        )

    def _from_entity(self, rec: MealRecommendation) -> MealRecommendationModel:
        return MealRecommendationModel(
            id=UUID(rec.id.value),
            user_id=UUID(rec.user_id.value),
            generated_for_date=rec.generated_for_date,
            body=rec.body,
            tips=rec.tips,
            created_at=rec.created_at,
        )

    # ------------------------------------------------------------------
    # Port 実装
    # ------------------------------------------------------------------

    def get_by_user_and_date(
        self,
        user_id: UserId,
        generated_for_date: DateType,
    ) -> MealRecommendation | None:
        """
        (user_id, generated_for_date) で 1 件取得する。

        - 同一日に複数存在する場合は、最も新しい created_at を返す。
        """
        model = (
            self._session.query(MealRecommendationModel)
            .filter(
                MealRecommendationModel.user_id == UUID(user_id.value),
                MealRecommendationModel.generated_for_date == generated_for_date,
            )
            .order_by(MealRecommendationModel.created_at.desc())
            .one_or_none()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def list_recent(
        self,
        user_id: UserId,
        limit: int,
    ) -> Sequence[MealRecommendation]:
        """
        指定ユーザーの最新の MealRecommendation を新しい順に最大 limit 件返す。
        """
        models: Sequence[MealRecommendationModel] = (
            self._session.query(MealRecommendationModel)
            .filter(
                MealRecommendationModel.user_id == UUID(user_id.value),
            )
            .order_by(
                MealRecommendationModel.generated_for_date.desc(),
                MealRecommendationModel.created_at.desc(),
            )
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def save(self, recommendation: MealRecommendation) -> None:
        """
        MealRecommendation を保存する。

        - id をキーに insert / update を吸収するため merge を利用。
        - トランザクション境界（commit/rollback）は UoW 側で管理する前提。
        """
        model = self._from_entity(recommendation)
        self._session.merge(model)
