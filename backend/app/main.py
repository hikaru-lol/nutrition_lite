from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.domain.auth import errors as auth_errors
from app.domain.meal import errors as meal_domain_errors
from app.application.target import errors as target_app_errors
from app.domain.target import errors as target_domain_errors
from app.api.http.errors import auth_error_handler, validation_error_handler
from app.api.http.errors import target_error_handler, target_domain_error_handler
from app.api.http.errors import meal_domain_error_handler
from app.api.http.routers.auth_route import router as auth_router
from app.api.http.routers.profile_route import router as profile_router
from app.api.http.routers.target_route import router as target_router
from app.api.http.routers.meal_route import router as meal_router


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="Nutrition Backend",
        version="0.1.0",
    )

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(profile_router, prefix="/api/v1")
    app.include_router(target_router, prefix="/api/v1")
    app.include_router(meal_router, prefix="/api/v1")
    app.add_exception_handler(auth_errors.AuthError, auth_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(
        target_app_errors.TargetError, target_error_handler)
    app.add_exception_handler(
        target_domain_errors.TargetDomainError, target_domain_error_handler)
    app.add_exception_handler(
        meal_domain_errors.MealDomainError, meal_domain_error_handler)
    return app


app = create_app()
