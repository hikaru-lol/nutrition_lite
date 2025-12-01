from __future__ import annotations

from datetime import date as DateType
from typing import Sequence

from app.application.meal.dto.daily_log_completion_dto import (
    DailyLogCompletionResultDTO,
)
from app.application.profile.ports.profile_repository_port import (
    ProfileRepositoryPort,
)
from app.application.meal.ports.uow_port import MealUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.meal.errors import (
    DailyLogProfileNotFoundError,
    InvalidMealsPerDayError,
)
from app.domain.meal.value_objects import MealType
from app.domain.meal.entities import FoodEntry
from app.application.profile.ports.profile_query_port import ProfileQueryPort


class CheckDailyLogCompletionUseCase:
    """
    1 日分の食事ログが「記録完了」しているかを判定する UseCase。

    - 対象:
        (user_id, date)
    - 完了条件:
        1. 対象ユーザーの Profile が存在し、meals_per_day >= 1 である。
        2. 該当日の FoodEntry のうち、
           meal_type == "main" の meal_index が
           {1, 2, ..., meals_per_day} をすべて含んでいる。

    - エッジケース:
        - Profile が存在しない → DailyLogProfileNotFoundError
        - meals_per_day < 1 → InvalidMealsPerDayError
    """

    def __init__(
        self,
        profile_query: ProfileQueryPort,
        meal_uow: MealUnitOfWorkPort,
    ) -> None:
        self._profile_query = profile_query
        self._meal_uow = meal_uow

    def execute(
        self,
        user_id: UserId,
        date_: DateType,
    ) -> DailyLogCompletionResultDTO:
        # --- 1. Profile 取得（なければエラー） ------------------------
        profile = self._profile_query.get_profile_for_daily_log(user_id)
        if profile is None:
            raise DailyLogProfileNotFoundError(
                f"Profile not found for user_id={user_id.value}"
            )

        meals_per_day = profile.meals_per_day
        if meals_per_day is None or meals_per_day < 1:
            raise InvalidMealsPerDayError(
                f"Invalid meals_per_day={meals_per_day} for user_id={user_id.value}"
            )

        # --- 2. 当日の FoodEntry（main のみ）を取得 -------------------
        with self._meal_uow as uow:
            entries: Sequence[FoodEntry] = uow.food_entry_repo.list_by_user_and_date(
                user_id=user_id,
                date=date_,
            )

        main_indices: set[int] = set()

        for e in entries:
            # snack は完了条件から除外
            if e.meal_type != MealType("main"):
                continue

            # meal_index が None / 範囲外のものは、基本的に入り得ない前提だが
            # 念のため範囲チェックを入れておく。
            if e.meal_index is None:
                # domain レベルでは InvalidMealIndexError を投げているはずなので、
                # ここでは単にスキップでもよいが、バグ検知のため ValueError にしてもよい。
                continue

            if not (1 <= e.meal_index <= meals_per_day):
                # ここも本来起きない前提だが、データ不整合検知のため warning/例外にしてもよい。
                continue

            main_indices.add(e.meal_index)

        # --- 3. 必要なインデックス集合と比較 -------------------------
        required_indices = set(range(1, meals_per_day + 1))
        missing_indices = sorted(required_indices - main_indices)
        filled_indices = sorted(main_indices & required_indices)

        is_completed = len(missing_indices) == 0

        # --- 4. DTO で返す -------------------------------------------
        return DailyLogCompletionResultDTO(
            user_id=user_id,
            date=date_,
            meals_per_day=meals_per_day,
            is_completed=is_completed,
            filled_indices=filled_indices,
            missing_indices=missing_indices,
        )
