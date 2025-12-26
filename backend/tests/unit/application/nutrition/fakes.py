from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from app.application.nutrition.ports.meal_entry_query_port import MealEntryQueryPort
from app.application.nutrition.ports.meal_nutrition_repository_port import (
    MealNutritionSummaryRepositoryPort,
)
from app.application.nutrition.ports.daily_nutrition_repository_port import (
    DailyNutritionSummaryRepositoryPort,
)
from app.application.nutrition.ports.daily_report_repository_port import (
    DailyNutritionReportRepositoryPort,
)
from app.application.nutrition.ports.daily_report_generator_port import (
    DailyNutritionReportGeneratorPort,
)
from app.application.nutrition.ports.nutrition_estimator_port import (
    NutritionEstimatorPort,
)
from app.application.nutrition.ports.uow_port import (
    DailyNutritionUnitOfWorkPort,
    NutritionReportUnitOfWorkPort,
)
from app.application.auth.ports.plan_checker_port import PlanCheckerPort
from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.meal.value_objects import MealType
from app.domain.nutrition.meal_nutrition import (
    MealNutritionSummary,
    MealNutrientIntake,
)
from app.domain.nutrition.daily_nutrition import DailyNutritionSummary
from app.domain.nutrition.daily_report import DailyNutritionReport
from app.application.nutrition.dto.daily_report_llm_dto import (
    DailyReportLLMInput,
    DailyReportLLMOutput,
)
from app.domain.target.value_objects import (
    NutrientCode,
    NutrientAmount,
    NutrientSource,
)
from tests.fakes.meal_uow import FakeMealUnitOfWork


class FakeMealEntryQueryService(MealEntryQueryPort):
    """インメモリのMealEntryQueryService"""

    def __init__(self, meal_uow: FakeMealUnitOfWork) -> None:
        self._meal_uow = meal_uow

    def list_entries_for_meal(
        self,
        user_id: UserId,
        date_: date,
        meal_type: MealType,
        meal_index: int | None,
    ) -> Sequence[FoodEntry]:
        with self._meal_uow as uow:
            return list(
                uow.food_entry_repo.list_by_user_date_type_index(
                    user_id=user_id,
                    target_date=date_,
                    meal_type=meal_type,
                    meal_index=meal_index,
                )
            )


class FakeNutritionEstimator(NutritionEstimatorPort):
    """インメモリのNutritionEstimator - 全ての栄養素を含む固定値を返す"""

    def estimate_for_entries(
        self,
        user_id: UserId,
        date: date,
        entries: Sequence[FoodEntry],
    ) -> list[MealNutrientIntake]:
        # 簡単な固定値を返す（全ての栄養素を含む）
        total_amount = (
            sum(e.amount_value or 0.0 for e in entries) if entries else 0.0
        )
        source = NutrientSource("llm")

        # 全ての栄養素を含む必要がある（エントリが0件でも全て0で返す）
        return [
            MealNutrientIntake(
                code=NutrientCode.PROTEIN,
                amount=NutrientAmount(value=total_amount * 0.20, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.FAT,
                amount=NutrientAmount(value=total_amount * 0.10, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.CARBOHYDRATE,
                amount=NutrientAmount(value=total_amount * 0.50, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.WATER,
                amount=NutrientAmount(value=total_amount * 0.10, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.FIBER,
                amount=NutrientAmount(value=total_amount * 0.05, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.SODIUM,
                amount=NutrientAmount(value=total_amount * 0.05, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.IRON,
                amount=NutrientAmount(value=total_amount * 0.05, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.CALCIUM,
                amount=NutrientAmount(value=total_amount * 0.05, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.VITAMIN_D,
                amount=NutrientAmount(value=total_amount * 0.05, unit="g"),
                source=source,
            ),
            MealNutrientIntake(
                code=NutrientCode.POTASSIUM,
                amount=NutrientAmount(value=total_amount * 0.05, unit="g"),
                source=source,
            ),
        ]


class FakeMealNutritionRepository(MealNutritionSummaryRepositoryPort):
    """インメモリのMealNutritionSummaryRepository"""

    def __init__(self) -> None:
        self._summaries: list[MealNutritionSummary] = []

    def get_by_user_date_meal(
        self,
        *,
        user_id: UserId,
        target_date: date,
        meal_type: MealType,
        meal_index: int | None,
    ) -> MealNutritionSummary | None:
        user_id_value = getattr(user_id, "value", str(user_id))
        for s in self._summaries:
            if (
                getattr(s.user_id, "value", str(s.user_id)) == user_id_value
                and s.date == target_date
                and s.meal_type == meal_type
                and s.meal_index == meal_index
            ):
                return s
        return None

    def list_by_user_and_date(
        self,
        *,
        user_id: UserId,
        target_date: date,
    ) -> Sequence[MealNutritionSummary]:
        user_id_value = getattr(user_id, "value", str(user_id))
        return [
            s
            for s in self._summaries
            if getattr(s.user_id, "value", str(s.user_id)) == user_id_value
            and s.date == target_date
        ]

    def save(self, summary: MealNutritionSummary) -> None:
        # 既存のものを削除して追加（upsert）
        self._summaries = [
            s
            for s in self._summaries
            if not (
                s.user_id == summary.user_id
                and s.date == summary.date
                and s.meal_type == summary.meal_type
                and s.meal_index == summary.meal_index
            )
        ]
        self._summaries.append(summary)


class FakeDailyNutritionRepository(DailyNutritionSummaryRepositoryPort):
    """インメモリのDailyNutritionSummaryRepository"""

    def __init__(self) -> None:
        self._summaries: dict[str, DailyNutritionSummary] = {}

    def get_by_user_and_date(
        self,
        *,
        user_id: UserId,
        target_date: date,
    ) -> DailyNutritionSummary | None:
        user_id_value = getattr(user_id, "value", str(user_id))
        key = f"{user_id_value}:{target_date}"
        return self._summaries.get(key)

    def list_by_user_and_range(
        self,
        *,
        user_id: UserId,
        start_date: date,
        end_date: date,
    ) -> Sequence[DailyNutritionSummary]:
        user_id_value = getattr(user_id, "value", str(user_id))
        return [
            s
            for s in self._summaries.values()
            if getattr(s.user_id, "value", str(s.user_id)) == user_id_value
            and start_date <= s.date <= end_date
        ]

    def save(self, summary: DailyNutritionSummary) -> None:
        user_id_value = getattr(summary.user_id, "value", str(summary.user_id))
        key = f"{user_id_value}:{summary.date}"
        self._summaries[key] = summary


class FakeNutritionUnitOfWork(NutritionReportUnitOfWorkPort):
    """インメモリのNutritionUnitOfWork"""

    def __init__(
        self,
        meal_nutrition_repo: MealNutritionSummaryRepositoryPort | None = None,
        daily_nutrition_repo: DailyNutritionSummaryRepositoryPort | None = None,
        daily_report_repo: DailyNutritionReportRepositoryPort | None = None,
    ) -> None:
        self.meal_nutrition_repo = (
            meal_nutrition_repo or FakeMealNutritionRepository()
        )
        self.daily_nutrition_repo = (
            daily_nutrition_repo or FakeDailyNutritionRepository()
        )
        self.daily_report_repo = (
            daily_report_repo or FakeDailyNutritionReportRepository()
        )
        self._committed = False

    def __enter__(self) -> "FakeNutritionUnitOfWork":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    def commit(self) -> None:
        self._committed = True

    def rollback(self) -> None:
        self._committed = False


class FakePlanChecker(PlanCheckerPort):
    """常にプレミアム機能を許可するFake実装"""

    def ensure_premium_feature(self, user_id: UserId) -> None:
        # テストでは常に許可
        pass


class FakeDailyNutritionReportRepository(DailyNutritionReportRepositoryPort):
    """インメモリのDailyNutritionReportRepository"""

    def __init__(self) -> None:
        self._reports: dict[str, DailyNutritionReport] = {}

    def get_by_user_and_date(
        self,
        user_id: UserId,
        target_date: date,
    ) -> DailyNutritionReport | None:
        user_id_value = getattr(user_id, "value", str(user_id))
        key = f"{user_id_value}:{target_date}"
        return self._reports.get(key)

    def list_recent(
        self,
        user_id: UserId,
        limit: int,
    ) -> Sequence[DailyNutritionReport]:
        user_id_value = getattr(user_id, "value", str(user_id))
        reports = [
            r
            for r in self._reports.values()
            if getattr(r.user_id, "value", str(r.user_id)) == user_id_value
        ]
        reports.sort(key=lambda r: r.date, reverse=True)
        return reports[:limit]

    def save(self, report: DailyNutritionReport) -> None:
        user_id_value = getattr(report.user_id, "value", str(report.user_id))
        key = f"{user_id_value}:{report.date}"
        self._reports[key] = report


class FakeDailyNutritionReportGenerator(DailyNutritionReportGeneratorPort):
    """インメモリのDailyNutritionReportGenerator - 固定値を返す"""

    def generate(
        self, input: DailyReportLLMInput
    ) -> DailyReportLLMOutput:
        date_str = input.date.isoformat()
        summary = f"{date_str} の食事は、全体としてバランスよく摂取できました。"
        good = [
            "たんぱく質を十分に摂取できています。",
            "野菜・果物からのビタミン・ミネラルが取れています。",
        ]
        improvement = [
            "水分摂取量がやや少ない可能性があります。",
            "脂質の質（飽和脂肪酸 / 不飽和脂肪酸）に少し注意してみましょう。",
        ]
        tomorrow = [
            "朝食でたんぱく質を意識的に摂る。",
            "1 日を通してこまめに水分補給する。",
        ]

        return DailyReportLLMOutput(
            summary=summary,
            good_points=good,
            improvement_points=improvement,
            tomorrow_focus=tomorrow,
        )
