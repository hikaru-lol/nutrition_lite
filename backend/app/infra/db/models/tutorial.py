"""チュートリアル機能のSQLAlchemyモデル"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from app.infra.db.base import Base


class TutorialCompletionModel(Base):
    """チュートリアル完了記録テーブル

    レコードの存在 = 完了を表す極小テーブル
    """
    __tablename__ = "tutorial_completions"

    user_id = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    tutorial_id = sa.Column(
        sa.String(50),
        primary_key=True,
        nullable=False,
    )
    completed_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )
    created_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("CURRENT_TIMESTAMP"),
        onupdate=sa.text("CURRENT_TIMESTAMP"),
    )

    # インデックス（パフォーマンス最適化）
    __table_args__ = (
        sa.Index("ix_tutorial_completions_user_id", "user_id"),
    )