from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from app.infra.db.base import Base


class MealRecommendationModel(Base):
    """
    MealRecommendation 用の SQLAlchemy モデル。

    - 1ユーザー & 1日あたり高々1件の提案を表現する。
    """

    __tablename__ = "meal_recommendations"

    # NOTE: as_uuid=True にして Python 側では uuid.UUID として扱う
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # この日までの履歴（通常は「今日」）を基準にした提案
    generated_for_date = Column(Date, nullable=False, index=True)

    # メインの提案文
    body = Column(Text, nullable=False)

    # 実行可能なアクション（箇条書き）
    # tips は ARRAY(Text) / ARRAY(String) / JSONB など好みでOK
    tips = Column(ARRAY(Text), nullable=False, default=list)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # Entity から渡す場合は上書きされる
    )

    __table_args__ = (
        # 同じユーザー & 同じ generated_for_date で高々1件
        UniqueConstraint("user_id", "generated_for_date",
                         name="uq_meal_recommendation_user_date"),
    )
