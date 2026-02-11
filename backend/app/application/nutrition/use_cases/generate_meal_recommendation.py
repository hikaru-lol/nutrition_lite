from __future__ import annotations

from dataclasses import dataclass
from datetime import date as DateType

from app.application.auth.ports.clock_port import ClockPort
from app.application.nutrition.ports.recommendation_generator_port import (
    MealRecommendationGeneratorPort,
)
from app.application.auth.ports.plan_checker_port import PlanCheckerPort
from app.application.profile.ports.profile_query_port import ProfileQueryPort, ProfileForRecommendation
from app.application.nutrition.ports.uow_port import NutritionUnitOfWorkPort

from app.application.nutrition.dto.meal_recommendation_llm_dto import (
    MealRecommendationLLMInput,
)

from app.domain.auth.value_objects import UserId
from app.domain.meal.errors import DailyLogProfileNotFoundError
from app.domain.nutrition.errors import (
    NotEnoughDailyReportsError,
    MealRecommendationCooldownError,
    MealRecommendationDailyLimitError,
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
        min_required_days: int = 1,
        max_lookup_days: int = 5,
        plan_checker: PlanCheckerPort | None = None,
        cooldown_minutes: int = 30,
        daily_limit: int = 5,
    ) -> None:
        self._profile_query = profile_query
        self._nutrition_uow = nutrition_uow
        self._generator = generator
        self._clock = clock
        self._min_required_days = min_required_days
        self._max_lookup_days = max_lookup_days
        self._plan_checker = plan_checker
        self._cooldown_minutes = cooldown_minutes
        self._daily_limit = daily_limit

    def execute(self, input: GenerateMealRecommendationInput) -> MealRecommendation:
        import logging
        logger = logging.getLogger(__name__)

        # --- 0. プレミアム機能チェック --------------------------------
        if self._plan_checker:
            self._plan_checker.ensure_premium_feature(input.user_id)

        user_id = input.user_id
        base_date = input.base_date or self._clock.now().date()

        logger.info(f"Generate meal recommendation: user_id={user_id.value}, date={base_date}, cooldown_minutes={self._cooldown_minutes}, daily_limit={self._daily_limit}")

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
            # 制約チェック1: 日次制限
            current_count = uow.meal_recommendation_repo.count_by_user_and_date(
                user_id=user_id,
                generated_for_date=base_date,
            )
            logger.info(f"Daily limit check: current_count={current_count}, daily_limit={self._daily_limit}")
            if current_count >= self._daily_limit:
                logger.warning(f"Daily limit exceeded: {current_count}/{self._daily_limit}")
                raise MealRecommendationDailyLimitError(
                    current_count=current_count,
                    limit=self._daily_limit,
                )

            # 制約チェック2: クールダウン期間（cooldown_minutes=0の場合はスキップ）
            if self._cooldown_minutes > 0:
                logger.info(f"Cooldown check enabled: cooldown_minutes={self._cooldown_minutes}")
                latest_recommendation = uow.meal_recommendation_repo.get_latest_by_user(
                    user_id=user_id
                )
                if latest_recommendation is not None:
                    from datetime import timedelta
                    now = self._clock.now()
                    wait_until = latest_recommendation.created_at + timedelta(minutes=self._cooldown_minutes)
                    logger.info(f"Latest recommendation: {latest_recommendation.created_at}, wait_until: {wait_until}, now: {now}")

                    if now < wait_until:
                        remaining_minutes = int((wait_until - now).total_seconds() / 60)
                        logger.warning(f"Cooldown period active: remaining_minutes={remaining_minutes}")
                        raise MealRecommendationCooldownError(
                            wait_until=wait_until,
                            remaining_minutes=remaining_minutes,
                        )
                else:
                    logger.info("No previous recommendations found, cooldown check passed")
            else:
                logger.info("Cooldown check disabled (cooldown_minutes=0)")

            # 直近最大5日分の DailyNutritionReport を取得
            recent_reports = list(
                uow.daily_report_repo.list_recent(
                    user_id=user_id,
                    limit=self._max_lookup_days,
                )
            )
            if len(recent_reports) < self._min_required_days:
                raise NotEnoughDailyReportsError(
                    f"Need at least {self._min_required_days} daily reports, "
                    f"but got {len(recent_reports)} for user_id={user_id.value}."
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

            # DTO -> ドメインエンティティ変換
            from app.domain.nutrition.meal_recommendation import RecommendedMeal
            recommended_meals = [
                RecommendedMeal(
                    title=meal.title,
                    description=meal.description,
                    ingredients=meal.ingredients,
                    nutrition_focus=meal.nutrition_focus,
                )
                for meal in llm_output.recommended_meals
            ]

            recommendation = MealRecommendation.create(
                user_id=user_id,
                generated_for_date=base_date,
                body=llm_output.body,
                tips=llm_output.tips,
                recommended_meals=recommended_meals,
                created_at=now,
            )

            # --- 永続化 ---------------------------------------------
            uow.meal_recommendation_repo.save(recommendation)
            # commit / rollback は UoW.__exit__ が担当

        return recommendation
