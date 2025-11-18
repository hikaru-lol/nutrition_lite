from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.domain.auth import errors as auth_errors
from app.api.http.errors import auth_error_handler, validation_error_handler

from app.api.http.routers.auth_route import router as auth_router
from app.infra.db.base import Base, engine


def create_app() -> FastAPI:
    app = FastAPI(
        title="Nutrition Backend",
        version="0.1.0",
    )

    # 開発環境向け: 自動テーブル作成
    Base.metadata.create_all(bind=engine)

    app.include_router(auth_router, prefix="/api/v1")

    app.add_exception_handler(auth_errors.AuthError, auth_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)

    return app


app = create_app()
