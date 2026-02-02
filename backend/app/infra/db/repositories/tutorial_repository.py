"""チュートリアルリポジトリ実装"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.application.tutorial.ports.tutorial_repository_port import TutorialRepositoryPort
from app.domain.tutorial.value_objects import TutorialCompletion, TutorialId, UserId
from app.infra.db.models.tutorial import TutorialCompletionModel

if TYPE_CHECKING:
    from uuid import UUID


class SqlAlchemyTutorialRepository(TutorialRepositoryPort):
    """SQLAlchemyを使用したチュートリアルリポジトリ実装"""

    def __init__(self, session: Session):
        self._session = session

    def add(self, completion: TutorialCompletion) -> None:
        """チュートリアル完了記録を追加

        重複する場合は何もしない（冪等性）
        """
        # 既に存在する場合はスキップ
        existing = self._session.execute(
            sa.select(TutorialCompletionModel).where(
                TutorialCompletionModel.user_id == completion.user_id,
                TutorialCompletionModel.tutorial_id == completion.tutorial_id,
            )
        ).scalar_one_or_none()

        if existing:
            return  # 既に存在するので何もしない

        # 新規追加
        model = TutorialCompletionModel(
            user_id=completion.user_id,
            tutorial_id=completion.tutorial_id,
            completed_at=completion.completed_at,
        )
        self._session.add(model)

    def exists(self, user_id: UserId, tutorial_id: TutorialId) -> bool:
        """チュートリアル完了記録が存在するかチェック"""
        count = self._session.scalar(
            sa.select(sa.func.count())
            .select_from(TutorialCompletionModel)
            .where(
                TutorialCompletionModel.user_id == user_id,
                TutorialCompletionModel.tutorial_id == tutorial_id,
            )
        )
        return count > 0

    def list_completed_by_user(self, user_id: UserId) -> list[TutorialCompletion]:
        """指定ユーザーの全完了記録を取得"""
        stmt = (
            sa.select(TutorialCompletionModel)
            .where(TutorialCompletionModel.user_id == user_id)
            .order_by(TutorialCompletionModel.completed_at.desc())
        )

        models = self._session.execute(stmt).scalars().all()

        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: TutorialCompletionModel) -> TutorialCompletion:
        """SQLAlchemyモデルをドメインエンティティに変換"""
        return TutorialCompletion(
            user_id=UserId(str(model.user_id)),
            tutorial_id=TutorialId(model.tutorial_id),
            completed_at=model.completed_at,
        )