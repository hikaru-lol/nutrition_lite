from __future__ import annotations

from datetime import date as DateType

from app.application.auth.ports.clock_port import ClockPort
from app.application.auth.ports.plan_checker_port import PlanCheckerPort
from app.application.nutrition.ports.daily_report_generator_port import (
    DailyNutritionReportGeneratorPort,
)
from app.application.nutrition.ports.uow_port import NutritionUnitOfWorkPort
from app.application.profile.ports.profile_query_port import ProfileQueryPort

from app.application.meal.dto.daily_log_completion_dto import (
    DailyLogCompletionResultDTO,
)
from app.application.nutrition.dto.daily_report_llm_dto import (
    DailyReportLLMInput,
    DailyReportLLMOutput,
)
from app.application.meal.use_cases.check_daily_log_completion import (
    CheckDailyLogCompletionUseCase,
)
from app.application.nutrition.use_cases.compute_daily_nutrition import (
    ComputeDailyNutritionSummaryUseCase,
)
from app.application.target.use_cases.ensure_daily_snapshot import (
    EnsureDailyTargetSnapshotUseCase,
)

from app.domain.auth.value_objects import UserId
from app.domain.nutrition.daily_report import DailyNutritionReport
from app.domain.nutrition.errors import (
    DailyLogNotCompletedError,
    DailyNutritionReportAlreadyExistsError,
)
from app.domain.profile.entities import Profile  # 実際のパスに合わせて調整
from app.domain.target.entities import DailyTargetSnapshot  # 実際のパスに合わせて調整
from app.domain.nutrition.daily_nutrition import DailyNutritionSummary
from app.domain.nutrition.meal_nutrition import MealNutritionSummary  # 実際のパスに合わせて


class GenerateDailyNutritionReportUseCase:
    """
    1 日分の栄養レポート (DailyNutritionReport) を生成して保存する UseCase。

    前提条件:
        - 該当日の食事ログが「記録完了」していること。
          （Profile.meals_per_day 回数の main meal が記録済み）

    処理フロー（概略）:
        1. 記録完了チェック (CheckDailyLogCompletionUseCase)
        2. 既存レポートの有無をチェック（あればエラー）
        3. Profile / DailyTargetSnapshot / DailyNutritionSummary / MealNutritionSummary を取得
        4. LLM ポートでレポート本文を生成
        5. DailyNutritionReport エンティティを組み立てて保存
    """

    def __init__(
        self,
        daily_log_uc: CheckDailyLogCompletionUseCase,
        profile_query: ProfileQueryPort,
        ensure_target_snapshot_uc: EnsureDailyTargetSnapshotUseCase,
        daily_nutrition_uc: ComputeDailyNutritionSummaryUseCase,
        nutrition_uow: NutritionUnitOfWorkPort,
        report_generator: DailyNutritionReportGeneratorPort,
        clock: ClockPort,
        plan_checker: PlanCheckerPort,
    ) -> None:
        self._daily_log_uc = daily_log_uc
        self._profile_query = profile_query
        self._ensure_target_snapshot_uc = ensure_target_snapshot_uc
        self._daily_nutrition_uc = daily_nutrition_uc
        self._uow = nutrition_uow
        self._report_generator = report_generator
        self._clock = clock
        self._plan_checker = plan_checker

    def execute(
        self,
        user_id: UserId,
        date_: DateType,
    ) -> DailyNutritionReport:
        """
        指定した (user_id, date) の DailyNutritionReport を生成して保存する。

        - 成功時: 新しく作成された DailyNutritionReport を返す。
        - 失敗時:
            - DailyLogNotCompletedError
            - DailyNutritionReportAlreadyExistsError
            - ProfileNotFound / TargetSnapshotNotFound 等（各 Repo / UC 由来）
            - PremiumFeatureRequiredError（プレミアム機能が不足している場合）
        """

        # --- 0. プレミアム機能チェック --------------------------------
        self._plan_checker.ensure_premium_feature(user_id)

        # --- 1. 記録完了チェック --------------------------------------
        completion: DailyLogCompletionResultDTO = self._daily_log_uc.execute(
            user_id=user_id,
            date_=date_,
        )
        if not completion.is_completed:
            # 「あとどのインデックスが足りないか」などをメッセージに含めると親切
            raise DailyLogNotCompletedError(
                f"Daily log not completed for user_id={user_id.value}, date={date_}. "
                f"missing_indices={completion.missing_indices}"
            )

        # --- 2. 既存レポートの有無をチェック -------------------------
        existing = self._uow.daily_report_repo.get_by_user_and_date(
            user_id=user_id,
            target_date=date_,
        )
        if existing is not None:
            raise DailyNutritionReportAlreadyExistsError(
                f"DailyNutritionReport already exists for user_id={user_id.value}, date={date_}"
            )

        # --- 3. Profile / TargetSnapshot / Daily / Meal を取得 --------

        # 3-1. Profile
        profile: Profile | None = self._profile_query.get_profile_for_daily_log(
            user_id)
        if profile is None:
            # ここは既に DailyLog 側でも ProfileNotFound を投げている想定だが、
            # 念のため二重チェックしておく。
            from app.domain.meal.errors import DailyLogProfileNotFoundError

            raise DailyLogProfileNotFoundError(
                f"Profile not found for user_id={user_id.value}"
            )

        # 3-2. DailyTargetSnapshot
        # EnsureDailyTargetSnapshotUseCase 側で「なければ作る」を担保している前提。
        target_snapshot: DailyTargetSnapshot = self._ensure_target_snapshot_uc.execute(
            user_id=user_id,
            date_=date_,
        )

        # 3-3. DailyNutritionSummary（なければ再計算）
        daily_summary: DailyNutritionSummary = self._daily_nutrition_uc.execute(
            user_id=user_id,
            date_=date_,
        )

        # 3-4. その日の MealNutritionSummary 一覧
        meal_summaries: list[MealNutritionSummary] = list(
            self._uow.meal_nutrition_repo.list_by_user_and_date(
                user_id=user_id,
                target_date=date_,
            )
        )

        # --- 4. LLM 入力 DTO を組み立ててレポート生成 ---------------

        llm_input = DailyReportLLMInput(
            user_id=user_id,
            date=date_,
            profile=profile,
            target_snapshot=target_snapshot,
            daily_summary=daily_summary,
            meal_summaries=meal_summaries,
        )

        llm_output: DailyReportLLMOutput = self._report_generator.generate(
            llm_input)

        # --- 5. DailyNutritionReport エンティティを組み立て ---------

        report = DailyNutritionReport.create(
            user_id=user_id,
            date=date_,
            summary=llm_output.summary,
            good_points=llm_output.good_points,
            improvement_points=llm_output.improvement_points,
            tomorrow_focus=llm_output.tomorrow_focus,
            created_at=self._clock.now(),
        )

        # --- 6. 保存 -------------------------------------------------
        self._uow.daily_report_repo.save(report)

        return report
