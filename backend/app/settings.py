# app/settings.py

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

    # Cookie / CORS 用（後で必要に応じて拡張）
    BACKEND_DOMAIN: str = os.getenv("BACKEND_DOMAIN", "localhost")
    COOKIE_SECURE: bool = _env_bool(
        "COOKIE_SECURE", False)  # prod では True にする想定
    COOKIE_SAMESITE: str = os.getenv(
        "COOKIE_SAMESITE", "lax")  # "lax" or "none"

    # JWT / Auth
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_TTL_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_TTL_MINUTES", "15"))
    REFRESH_TOKEN_TTL_DAYS: int = int(os.getenv("REFRESH_TOKEN_TTL_DAYS", "7"))

    # DB
    # NOTE: 本番では必ず env で上書きする前提。
    # CI / ローカルでは env がなければ sqlite in-memory で動くようにしている。
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+pysqlite:///:memory:")


settings = Settings()
