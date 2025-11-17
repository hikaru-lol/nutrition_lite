from fastapi import FastAPI
from app.api.http.routers.auth import router as auth_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Nutrition Backend",
        version="0.1.0",
    )

    app.include_router(auth_router, prefix="/api/v1")

    return app


app = create_app()
