from __future__ import annotations

from datetime import date as DateType

from app.application.auth.ports.clock_port import ClockPort
from app.application.nutrition.dto.recommendation_llm_dto import (
    MealRecommendationLLMInput,
    MealRecommendationLLMOutput,
)
from app.application.nutrition.ports.daily_report_repository_port import (
    DailyNutritionReportRepositoryPort,
)
from app.application.nutrition.ports.recommendation_generator_port import (
    MealRecommendationGeneratorPort,
)
from app.application.nutrition.ports.recommendation_repository_port import (
    MealRecommendationRepositoryPort,
)
from app.application.profile.ports.profile_repository_port import (
    ProfileRepositoryPort,
)
from app.application.target.ports.target_repository_port import (
    TargetRepositoryPort,
)
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_report import DailyNutritionReport
from app.domain.nutrition.errors import (
    NotEnoughDailyReportsError,
    MealRecommendationAlreadyExistsError,
)
from app.domain.nutrition.recommendation import MealRecommendation
from app.domain.profile.entities import Profile  # パスは実装に合わせて
from app.domain.target.entities import TargetDefinition  # 実装に合わせて


class GenerateMealRecommendationUseCase:
    """
    直近 N 日分の DailyNutritionReport をもとに食事提案を生成する UseCase。

    想定フロー:
        1. ユーザーの Profile を取得（なければエラー or スキップ）
        2. 直近 N 日分の DailyNutritionReport を取得
           - N 未満なら NotEnoughDailyReportsError
        3. 今日（または base_date）に対する Recommendation が既にあれば MealRecommendationAlreadyExistsError
        4. LLM ポートに投げて MealRecommendationLLMOutput を得る
        5. MealRecommendation を作成して保存
    """

    def __init__(
        self,
        profile_repo: ProfileRepositoryPort,
        target_repo: TargetRepositoryPort,
        daily_report_repo: DailyNutritionReportRepositoryPort,
        recommendation_repo: MealRecommendationRepositoryPort,
        generator: MealRecommendationGeneratorPort,
        clock: ClockPort,
        required_days: int = 5,
    ) -> None:
        self._profile_repo = profile_repo
        self._target_repo = target_repo
        self._daily_report_repo = daily_report_repo
        self._recommendation_repo = recommendation_repo
        self._generator = generator
        self._clock = clock
        self._required_days = required_days

    def execute(
        self,
        user_id: UserId,
        base_date: DateType | None = None,
    ) -> MealRecommendation:
        """
        :param user_id: 対象ユーザー
        :param base_date: この日までのレポートをもとに生成する基準日。
                          None の場合は「今日 (clock.now().date())」を使用。
        """

        if base_date is None:
            base_date = self._clock.now().date()

        # --- 1. Profile ------------------------------------------------
        profile: Profile | None = self._profile_repo.get_by_user_id(user_id)
        if profile is None:
            # 仕様によってはここでスキップでも良いが、
            # 今は明示的に例外にしておく。
            from app.domain.meal.errors import DailyLogProfileNotFoundError

            raise DailyLogProfileNotFoundError(
                f"Profile not found for user_id={user_id.value}"
            )

        # --- 2. 直近 N 日の DailyNutritionReport ----------------------
        # DailyNutritionReportRepositoryPort の list_recent は
        # 「新しい順で max N 件」を返す想定。
        recent_reports: list[DailyNutritionReport] = list(
            self._daily_report_repo.list_recent(
                user_id=user_id, limit=self._required_days)
        )
        if len(recent_reports) < self._required_days:
            raise NotEnoughDailyReportsError(
                f"Need at least {self._required_days} daily reports, "
                f"but got {len(recent_reports)} for user_id={user_id.value}."
            )

        # 基準日は「直近 N 日の最後の日」としておくこともできるが、
        # ここでは引数 base_date を採用。
        generated_for_date = base_date

        # --- 3. 既存 Recommendation チェック -------------------------
        existing = self._recommendation_repo.get_by_user_and_date(
            user_id=user_id,
            generated_for_date=generated_for_date,
        )
        if existing is not None:
            raise MealRecommendationAlreadyExistsError(
                f"Recommendation already exists for user_id={user_id.value}, "
                f"generated_for_date={generated_for_date}"
            )

        # --- 4. アクティブ TargetDefinition を取得（あれば） --------
        # Active Target がない場合も提案は生成できるように Optional として扱う。
        active_target: TargetDefinition | None = self._target_repo.get_active(
            user_id=user_id
        )

        # --- 5. LLM 入力 DTO 構築 & 生成 -----------------------------
        llm_input = MealRecommendationLLMInput(
            user_id=user_id,
            base_date=generated_for_date,
            profile=profile,
            active_target=active_target,
            recent_reports=recent_reports,
        )

        llm_output: MealRecommendationLLMOutput = self._generator.generate(
            llm_input)

        # --- 6. Recommendation エンティティ構築 ----------------------
        recommendation = MealRecommendation.create(
            user_id=user_id,
            generated_for_date=generated_for_date,
            body=llm_output.body,
            tips=llm_output.tips,
            created_at=self._clock.now(),
        )

        # --- 7. 保存 --------------------------------------------------
        self._recommendation_repo.save(recommendation)

        return recommendation
