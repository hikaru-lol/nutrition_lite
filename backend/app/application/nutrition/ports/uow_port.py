from __future__ import annotations

from typing import Protocol

from app.application.common.ports.unit_of_work_port import UnitOfWorkPort
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


class MealNutritionUnitOfWorkPort(UnitOfWorkPort, Protocol):
    """
    Meal 単位の栄養サマリ (MealNutritionSummary) だけを扱う UoW。
    - ComputeMealNutritionUseCase などが使う想定。
    """
    meal_nutrition_repo: MealNutritionSummaryRepositoryPort


class DailyNutritionUnitOfWorkPort(MealNutritionUnitOfWorkPort, Protocol):
    """
    Meal + Daily の栄養サマリを扱う UoW。
    - ComputeDailyNutritionSummaryUseCase などが使う想定。
    """
    daily_nutrition_repo: DailyNutritionSummaryRepositoryPort


class NutritionReportUnitOfWorkPort(DailyNutritionUnitOfWorkPort, Protocol):
    """
    日次レポートまで扱う UoW。
    - GenerateDailyNutritionReportUseCase などが使う想定。
    """
    daily_report_repo: DailyNutritionReportRepositoryPort


class RecommendationUnitOfWorkPort(DailyNutritionUnitOfWorkPort, Protocol):
    """
    レコメンドまで扱う UoW。
    """
    meal_recommendation_repo: MealRecommendationRepositoryPort


class NutritionUnitOfWorkPort(
    RecommendationUnitOfWorkPort,
    NutritionReportUnitOfWorkPort,
    Protocol,
):
    """
    栄養ドメインの「全部入り」UoW。

    - 具体クラス(SqlAlchemyNutritionUnitOfWork) はこれを実装する
    - UseCase 側は必要に応じて MealNutritionUnitOfWorkPort /
      DailyNutritionUnitOfWorkPort / NutritionReportUnitOfWorkPort など
      “細い” 型を受け取って OK
    """
    ...
