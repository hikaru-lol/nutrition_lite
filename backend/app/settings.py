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

    # MinIO / S3 互換ストレージ
    raw_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
    if raw_endpoint.startswith("http://"):
        raw_endpoint = raw_endpoint[len("http://"):]
    elif raw_endpoint.startswith("https://"):
        raw_endpoint = raw_endpoint[len("https://"):]
    MINIO_ENDPOINT: str = raw_endpoint
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_USE_SSL: bool = _env_bool("MINIO_USE_SSL", False)
    MINIO_BUCKET_NAME: str = os.getenv(
        "MINIO_BUCKET_NAME",
        "nutrition-dev",
    )

    # DB
    # NOTE: 本番では必ず env で上書きする前提。
    # CI / ローカルでは env がなければ sqlite in-memory で動くようにしている。
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+pysqlite:///:memory:")

    # テストで Fake を使うかどうか切り替えるためのフラグ
    USE_FAKE_INFRA: bool = _env_bool("USE_FAKE_INFRA", True)


settings = Settings()
