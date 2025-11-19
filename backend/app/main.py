from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.domain.auth import errors as auth_errors
from app.api.http.errors import auth_error_handler, validation_error_handler

from app.api.http.routers.auth_route import router as auth_router


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

    app.add_exception_handler(auth_errors.AuthError, auth_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)

    return app


app = create_app()
