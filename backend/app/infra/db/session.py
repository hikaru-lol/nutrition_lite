from __future__ import annotations

from typing import Generator

from sqlalchemy.orm import Session

from app.infra.db.base import SessionLocal


def create_session() -> Session:
    """
    生の Session を生成するヘルパー。
    DI やバッチ処理などからも使える。
    """
    return SessionLocal()


def get_db_session() -> Generator[Session, None, None]:
    """
    FastAPI の Depends で使うための DB セッション依存。
    1リクエストごとに新しい Session を開き、レスポンス後に閉じる。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
