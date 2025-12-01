from __future__ import annotations

from dataclasses import dataclass
from datetime import date as DateType

from app.application.auth.ports.clock_port import ClockPort
from app.application.nutrition.dto.meal_recommendation_llm_dto import (
    MealRecommendationLLMInput,
)
from app.application.profile.ports.profile_query_port import ProfileQueryPort, ProfileForRecommendation
from app.application.nutrition.ports.recommendation_generator_port import (
    MealRecommendationGeneratorPort,
)
from app.application.nutrition.ports.uow_port import NutritionUnitOfWorkPort

from app.domain.auth.value_objects import UserId
from app.domain.meal.errors import DailyLogProfileNotFoundError
from app.domain.nutrition.errors import (
    NotEnoughDailyReportsError,
    MealRecommendationAlreadyExistsError,
)
from app.domain.nutrition.meal_recommendation import MealRecommendation


@dataclass(slots=True)
class GenerateMealRecommendationInput:
    """
    提案生成 UC の入力。

    - base_date: None の場合は clock.now().date() を使用。
    """

    user_id: UserId
    base_date: DateType | None = None


class GenerateMealRecommendationUseCase:
    """
    直近 N 日分の日次レポートをもとに MealRecommendation を生成・保存する UseCase。

    - 他コンテキストの Profile は ProfileQueryPort 経由
    - DailyNutritionReport / MealRecommendation など栄養ドメインの書き込みは NutritionUnitOfWorkPort 経由
    """

    def __init__(
        self,
        profile_query: ProfileQueryPort,
        nutrition_uow: NutritionUnitOfWorkPort,
        generator: MealRecommendationGeneratorPort,
        clock: ClockPort,
        required_days: int = 5,
    ) -> None:
        self._profile_query = profile_query
        self._nutrition_uow = nutrition_uow
        self._generator = generator
        self._clock = clock
        self._required_days = required_days

    def execute(self, input: GenerateMealRecommendationInput) -> MealRecommendation:
        user_id = input.user_id
        base_date = input.base_date or self._clock.now().date()

        # --- Profile 取得（QueryPort 経由） ---------------------------
        profile: ProfileForRecommendation | None = self._profile_query.get_profile_for_recommendation(
            user_id
        )
        if profile is None:
            # 既存の DailyLogProfileNotFoundError を使って整合性を保つ
            raise DailyLogProfileNotFoundError(
                f"Profile not found for user_id={user_id.value}"
            )

        # --- Nutrition UoW 経由で DailyReport / Recommendation を操作 ---
        with self._nutrition_uow as uow:
            # 直近 N 日分の DailyNutritionReport を取得
            recent_reports = list(
                uow.daily_report_repo.list_recent(
                    user_id=user_id,
                    limit=self._required_days,
                )
            )
            if len(recent_reports) < self._required_days:
                raise NotEnoughDailyReportsError(
                    f"Need at least {self._required_days} daily reports, "
                    f"but got {len(recent_reports)} for user_id={user_id.value}."
                )

            # 当日の Recommendation 既存チェック
            existing = uow.meal_recommendation_repo.get_by_user_and_date(
                user_id=user_id,
                generated_for_date=base_date,
            )
            if existing is not None:
                raise MealRecommendationAlreadyExistsError(
                    f"MealRecommendation already exists for user_id={user_id.value}, "
                    f"date={base_date}"
                )

            # --- LLM 入力 DTO 構築 ------------------------------------
            llm_input = MealRecommendationLLMInput(
                user_id=user_id,
                base_date=base_date,
                profile=profile,
                recent_reports=recent_reports,
            )

            # --- LLM で提案生成 --------------------------------------
            llm_output = self._generator.generate(llm_input)

            # --- MealRecommendation エンティティ生成 -----------------
            now = self._clock.now()
            recommendation = MealRecommendation.create(
                user_id=user_id,
                generated_for_date=base_date,
                body=llm_output.body,
                tips=llm_output.tips,
                created_at=now,
            )

            # --- 永続化 ---------------------------------------------
            uow.meal_recommendation_repo.save(recommendation)
            # commit / rollback は UoW.__exit__ が担当

        return recommendation
