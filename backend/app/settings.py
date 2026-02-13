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

    # ===== CORS =====
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")

    # ===== OpenAI API 関連 =====
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # --- OpenAI フィーチャーフラグ ---
    USE_OPENAI_TARGET_GENERATOR: bool = _env_bool(
        "USE_OPENAI_TARGET_GENERATOR", False)
    USE_OPENAI_NUTRITION_ESTIMATOR: bool = _env_bool(
        "USE_OPENAI_NUTRITION_ESTIMATOR", False)
    USE_OPENAI_DAILY_REPORT_GENERATOR: bool = _env_bool(
        "USE_OPENAI_DAILY_REPORT_GENERATOR", False)
    USE_OPENAI_MEAL_RECOMMENDATION_GENERATOR: bool = _env_bool(
        "USE_OPENAI_MEAL_RECOMMENDATION_GENERATOR", False)

    # --- OpenAI モデル設定 ---
    OPENAI_TARGET_MODEL: str = os.getenv(
        "OPENAI_TARGET_MODEL", "gpt-4o-mini")
    OPENAI_TARGET_TEMPERATURE: float = float(
        os.getenv("OPENAI_TARGET_TEMPERATURE", "0.2"))
    OPENAI_NUTRITION_MODEL: str = os.getenv(
        "OPENAI_NUTRITION_MODEL", "gpt-4o-mini")
    OPENAI_NUTRITION_TEMPERATURE: float = float(
        os.getenv("OPENAI_NUTRITION_TEMPERATURE", "0.1"))
    OPENAI_DAILY_REPORT_MODEL: str = os.getenv(
        "OPENAI_DAILY_REPORT_MODEL", "gpt-4o-mini")
    OPENAI_DAILY_REPORT_TEMPERATURE: float = float(
        os.getenv("OPENAI_DAILY_REPORT_TEMPERATURE", "0.4"))
    OPENAI_MEAL_RECOMMENDATION_MODEL: str = os.getenv(
        "OPENAI_MEAL_RECOMMENDATION_MODEL", "gpt-4o-mini")
    OPENAI_MEAL_RECOMMENDATION_TEMPERATURE: float = float(
        os.getenv("OPENAI_MEAL_RECOMMENDATION_TEMPERATURE", "0.4"))

    # ===== 食事推薦レート制限 =====
    MEAL_RECOMMENDATION_COOLDOWN_MINUTES: int = int(
        os.getenv("MEAL_RECOMMENDATION_COOLDOWN_MINUTES", "30"))
    MEAL_RECOMMENDATION_DAILY_LIMIT: int = int(
        os.getenv("MEAL_RECOMMENDATION_DAILY_LIMIT", "5"))

    # ===== Stripe API 関連 =====
    STRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_ID: str = os.getenv("STRIPE_PRICE_ID", "")
    STRIPE_CHECKOUT_SUCCESS_URL: str = os.getenv(
        "STRIPE_CHECKOUT_SUCCESS_URL", "")
    STRIPE_CHECKOUT_CANCEL_URL: str = os.getenv(
        "STRIPE_CHECKOUT_CANCEL_URL", "")
    STRIPE_PORTAL_RETURN_URL: str = os.getenv(
        "STRIPE_PORTAL_RETURN_URL", "")

    # ===== バッチジョブ =====
    JOB_RECOMMEND_BASE_DATE: str = os.getenv(
        "JOB_RECOMMEND_BASE_DATE", "")


settings = Settings()
