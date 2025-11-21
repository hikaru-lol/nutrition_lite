from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, DeclarativeMeta

from app.settings import settings  # ← ここが効くようになった


# ----------------------------
# SQLAlchemy 基本セットアップ
# ----------------------------

Base: DeclarativeMeta = declarative_base()

engine = create_engine(
    settings.DATABASE_URL,  # ← env or デフォルト sqlite
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)
