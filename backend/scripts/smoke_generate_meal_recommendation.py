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
from app.di.container import get_generate_meal_recommendation_use_case

# プロジェクトルート（backend/）を基準に .env を読む
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def main() -> None:
    # テスト用に .env から USER_ID を読む（なければ仮のID）
    user_id_raw = os.getenv("SMOKE_RECOMMEND_USER_ID",
                            "test-user-for-recommendation")
    base_date_str = os.getenv(
        "SMOKE_RECOMMEND_BASE_DATE")  # "YYYY-MM-DD" or None

    user_id = UserId(user_id_raw)
    base_date: DateType | None = (
        DateType.fromisoformat(base_date_str) if base_date_str else None
    )

    use_case: GenerateMealRecommendationUseCase = (
        get_generate_meal_recommendation_use_case()
    )

    print("=== Smoke test for GenerateMealRecommendationUseCase ===")
    print(f"user_id   = {user_id.value}")
    print(f"base_date = {base_date.isoformat() if base_date else '(today)'}")
    print()

    input_dto = GenerateMealRecommendationInput(
        user_id=user_id,
        base_date=base_date,
    )

    try:
        recommendation = use_case.execute(input_dto)
    except Exception as e:
        print("[ERROR] Failed to generate recommendation:", repr(e))
        return

    print("=== Generated MealRecommendation ===")
    print(f"generated_for_date: {recommendation.generated_for_date}")
    print()
    print("[BODY]")
    print(recommendation.body)
    print()
    print("[TIPS]")
    for idx, tip in enumerate(recommendation.tips, start=1):
        print(f"{idx}. {tip}")


if __name__ == "__main__":
    main()
