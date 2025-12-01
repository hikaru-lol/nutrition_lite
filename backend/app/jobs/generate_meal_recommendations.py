from __future__ import annotations

import os
from datetime import date as DateType
from pathlib import Path

from dotenv import load_dotenv

from app.application.nutrition.use_cases.generate_meal_recommendation import (
    GenerateMealRecommendationInput,
    GenerateMealRecommendationUseCase,
)
from app.domain.auth.value_objects import UserId
from app.domain.nutrition.errors import (
    NotEnoughDailyReportsError,
    MealRecommendationAlreadyExistsError,
)
from app.domain.meal.errors import DailyLogProfileNotFoundError
from app.di.container import (
    get_auth_uow,
    get_generate_meal_recommendation_use_case,
)

# プロジェクトルート（backend/）を基準に .env を読む
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _list_active_user_ids() -> list[UserId]:
    """
    Auth UoW 経由でアクティブユーザー一覧を取得する。

    - SqlAlchemyUserRepository に list_active_users() がある前提。
    - 無ければ TODO にしておいてもOK。
    """
    from app.application.auth.ports.uow_port import AuthUnitOfWorkPort

    uow: AuthUnitOfWorkPort = get_auth_uow()
    with uow as tx:
        users = tx.user_repo.list_active_users()  # TODO: 実装に合わせて名称調整
        return [user.id for user in users]


def main() -> None:
    # 今日の日付
    # GenerateMealRecommendationUseCase 側が None を today に解決するので省略も可
    base_date_str = os.getenv("JOB_RECOMMEND_BASE_DATE")
    base_date: DateType | None = (
        DateType.fromisoformat(base_date_str) if base_date_str else None
    )

    use_case: GenerateMealRecommendationUseCase = (
        get_generate_meal_recommendation_use_case()
    )

    user_ids = _list_active_user_ids()
    print("=== Job: GenerateMealRecommendations ===")
    print(f"target users: {len(user_ids)}")
    print(f"base_date   : {base_date.isoformat() if base_date else '(today)'}")
    print()

    for uid in user_ids:
        print(f"[User] {uid.value} ... ", end="", flush=True)
        try:
            input_dto = GenerateMealRecommendationInput(
                user_id=uid,
                base_date=base_date,
            )
            rec = use_case.execute(input_dto)
        except DailyLogProfileNotFoundError:
            print("SKIP (no profile)")
        except NotEnoughDailyReportsError:
            print("SKIP (not enough daily reports)")
        except MealRecommendationAlreadyExistsError:
            print("SKIP (already exists)")
        except Exception as e:
            print(f"ERROR ({type(e).__name__}: {e})")
        else:
            print(f"OK (generated for {rec.generated_for_date})")


if __name__ == "__main__":
    main()
