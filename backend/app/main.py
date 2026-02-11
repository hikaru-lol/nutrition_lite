from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware  # 追加: CORSミドルウェア

from app.domain.auth import errors as auth_errors
from app.domain.meal import errors as meal_domain_errors
from app.domain.nutrition import errors as nutrition_domain_errors
from app.domain.profile import errors as profile_domain_errors
from app.application.target import errors as target_app_errors
from app.domain.target import errors as target_domain_errors
from app.domain.calendar import errors as calendar_domain_errors
from app.api.http.errors import auth_error_handler, validation_error_handler
from app.api.http.errors import profile_domain_error_handler
from app.api.http.errors import target_error_handler, target_domain_error_handler
from app.api.http.errors import meal_domain_error_handler
from app.api.http.errors import nutrition_domain_error_handler
from app.api.http.errors import meal_slot_error_handler
from app.api.http.errors import calendar_domain_error_handler
from app.api.http.routers.auth_route import router as auth_router
from app.api.http.routers.profile_route import router as profile_router
from app.api.http.routers.target_route import router as target_router
from app.api.http.routers.meal_route import router as meal_router
from app.api.http.routers.nutrition_route import router as nutrition_router
from app.api.http.routers.daily_report_route import router as daily_report_router
from app.api.http.routers.calendar_route import router as calendar_router
from app.api.http.routers.billing_route import router as billing_router
from app.api.http.routers.tutorial_route import router as tutorial_router
from app.api.http.routers.meal_recommendation_route import router as meal_recommendation_router


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


def create_app() -> FastAPI:
    # Load environment variables from .env file
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path, override=False)

    configure_logging()
    app = FastAPI(
        title="Nutrition Backend",
        version="0.1.0",
    )

    # --- CORS設定 追加ここから ---
    # フロントエンドのURLを許可リストに追加
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # 本番環境のフロントエンドURLを追加
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        origins.append(frontend_url)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,       # 許可するオリジン
        allow_credentials=True,      # Cookie等の信用情報を含むリクエストを許可
        allow_methods=["*"],         # 全てのHTTPメソッド(GET, POST, PUT...)を許可
        allow_headers=["*"],         # 全てのヘッダーを許可
    )
    # --- CORS設定 追加ここまで ---

    @app.get("/api/v1/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/health/one-more")
    def health_one_more() -> dict:
        return {"status": "ok one more"}

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(profile_router, prefix="/api/v1")
    app.include_router(target_router, prefix="/api/v1")
    app.include_router(meal_router, prefix="/api/v1")
    app.include_router(nutrition_router, prefix="/api/v1")
    app.include_router(daily_report_router, prefix="/api/v1")
    app.include_router(calendar_router, prefix="/api/v1/calendar", tags=["calendar"])
    app.include_router(billing_router, prefix="/api/v1")
    app.include_router(tutorial_router, prefix="/api/v1")
    app.include_router(meal_recommendation_router, prefix="/api/v1")
    app.add_exception_handler(auth_errors.AuthError, auth_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(
        target_app_errors.TargetError, target_error_handler)
    app.add_exception_handler(
        target_domain_errors.TargetDomainError, target_domain_error_handler)
    app.add_exception_handler(
        meal_domain_errors.MealDomainError, meal_domain_error_handler)
    app.add_exception_handler(
        nutrition_domain_errors.NutritionDomainError, nutrition_domain_error_handler)
    app.add_exception_handler(
        meal_domain_errors.InvalidMealTypeError, meal_slot_error_handler)
    app.add_exception_handler(
        profile_domain_errors.ProfileError, profile_domain_error_handler)
    app.add_exception_handler(
        calendar_domain_errors.CalendarError, calendar_domain_error_handler)
    return app


app = create_app()
