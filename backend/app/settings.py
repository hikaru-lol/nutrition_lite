from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in ("1", "true", "yes", "on")


@dataclass
class Settings:
    # 環境名: local / dev / prod など
    ENV: str = os.getenv("ENV", "local")

    # Cookie / CORS 用（必要に応じて後で拡張）
    BACKEND_DOMAIN: str = os.getenv("BACKEND_DOMAIN", "localhost")
    COOKIE_SECURE: bool = _env_bool("COOKIE_SECURE", False)  # prod では True に
    COOKIE_SAMESITE: str = os.getenv(
        "COOKIE_SAMESITE", "lax")  # "lax" or "none"

    # JWT / Auth
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_TTL_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_TTL_MINUTES", "15"))
    REFRESH_TOKEN_TTL_DAYS: int = int(os.getenv("REFRESH_TOKEN_TTL_DAYS", "7"))

    # DB（他の場所でも使えるようにここに出しておく）
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+pysqlite:///:memory:")


settings = Settings()
