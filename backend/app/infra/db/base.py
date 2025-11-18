# app/infra/db/base.py

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.settings import settings


# SQLAlchemy Base（全モデルが継承するやつ）
Base = declarative_base()


# Engine（DB接続）
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)


# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)
