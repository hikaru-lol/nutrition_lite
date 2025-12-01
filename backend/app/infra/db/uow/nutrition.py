from __future__ import annotations

from typing import Callable

from sqlalchemy.orm import Session

from app.application.nutrition.ports.uow_port import NutritionUnitOfWorkPort
from app.application.nutrition.ports.meal_nutrition_repository_port import (
    MealNutritionSummaryRepositoryPort,
)
from app.application.nutrition.ports.daily_nutrition_repository_port import (
    DailyNutritionSummaryRepositoryPort,
)
from app.application.nutrition.ports.daily_report_repository_port import (
    DailyNutritionReportRepositoryPort,
)
from app.application.nutrition.ports.recommendation_repository_port import (
    MealRecommendationRepositoryPort,
)

from app.infra.db.session import create_session
from app.infra.db.uow.sqlalchemy_base import SqlAlchemyUnitOfWorkBase
from app.infra.db.repositories.meal_nutrition_repository import (
    SqlAlchemyMealNutritionSummaryRepository,
)
from app.infra.db.repositories.daily_nutrition_repository import (
    SqlAlchemyDailyNutritionSummaryRepository,
)
from app.infra.db.repositories.daily_nutrition_report_repository import (
    SqlAlchemyDailyNutritionReportRepository,
)
from app.infra.db.repositories.meal_recommendation_repository import (
    SqlAlchemyMealRecommendationRepository,
)


class SqlAlchemyNutritionUnitOfWork(SqlAlchemyUnitOfWorkBase, NutritionUnitOfWorkPort):
    """
    栄養ドメイン用の Unit of Work 実装。
    """

    meal_nutrition_repo: MealNutritionSummaryRepositoryPort
    daily_nutrition_repo: DailyNutritionSummaryRepositoryPort
    daily_report_repo: DailyNutritionReportRepositoryPort
    meal_recommendation_repo: MealRecommendationRepositoryPort

    def __init__(self, session_factory: Callable[[], Session] = create_session) -> None:
        super().__init__(session_factory)

    def _on_enter(self, session: Session) -> None:
        self.meal_nutrition_repo = SqlAlchemyMealNutritionSummaryRepository(
            session)
        self.daily_nutrition_repo = SqlAlchemyDailyNutritionSummaryRepository(
            session)
        self.daily_report_repo = SqlAlchemyDailyNutritionReportRepository(
            session)
        self.meal_recommendation_repo = SqlAlchemyMealRecommendationRepository(
            session)
