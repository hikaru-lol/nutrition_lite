from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ----------------------------
# DB URL の決定
# ----------------------------

# 優先順位:
# 1. 環境変数 DATABASE_URL
# 2. なければテスト・ローカル用に sqlite in-memory
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")

# ----------------------------
# SQLAlchemy 基本セットアップ
# ----------------------------

Base = declarative_base()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)
