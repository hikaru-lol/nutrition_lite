from __future__ import annotations

from fastapi import FastAPI

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

    return app


app = create_app()
