
from typing import Sequence

from app.domain.auth.entities import User  # 実際のパスに合わせて
from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.infra.db.repositories.user_repository import SqlAlchemyUserRepository  # 実装に合わせて
from app.application.nutrition.use_cases.generate_meal_recommendation import (
    GenerateMealRecommendationUseCase,
)
from app.di.container import (
    get_generate_meal_recommendation_use_case,
)
from app.domain.nutrition.errors import (
    NotEnoughDailyReportsError,
    MealRecommendationAlreadyExistsError,
)


def run_generate_meal_recommendations_job() -> None:
    """
    全ユーザーに対して食事提案を生成するバッチジョブ。

    - 直近 N 日分の日次レポートが揃っているユーザーのみ対象。
    - すでに本日の提案が存在する場合はスキップ。
    """

    uc: GenerateMealRecommendationUseCase = get_generate_meal_recommendation_use_case()

    users: Sequence[User] = get_auth_uow().user_repo.list_active_users()

    for user in users:
        user_id = user.id  # UserId 型 or 生 UUID → UseCase 側に合わせて変換

        try:
            # User エンティティの user.id が UserId の場合はそのまま、
            # UUID の場合は UserId(str(user.id)) に包むなどプロジェクト側に合わせて。
            recommendation = uc.execute(user_id=user_id)
            print(
                f"[OK] Generated recommendation for user_id={user_id} "
                f"date={recommendation.generated_for_date}"
            )
        except NotEnoughDailyReportsError:
            print(f"[SKIP] Not enough daily reports for user_id={user_id}")
        except MealRecommendationAlreadyExistsError:
            print(
                f"[SKIP] Recommendation already exists for user_id={user_id}")
        except Exception as e:
            print(
                f"[ERROR] Failed to generate recommendation for user_id={user_id}: {e}")
