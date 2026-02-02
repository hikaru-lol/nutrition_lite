"""チュートリアルリポジトリのポート"""

from __future__ import annotations

from typing import Protocol

from app.domain.tutorial.value_objects import TutorialCompletion, TutorialId, UserId


class TutorialRepositoryPort(Protocol):
    """チュートリアルリポジトリのインターフェース

    Simple CRUD operations for tutorial completions.
    """

    def add(self, completion: TutorialCompletion) -> None:
        """チュートリアル完了記録を追加

        Args:
            completion: 追加する完了記録

        Note:
            重複する場合は何もしない（冪等性）
        """
        ...

    def exists(self, user_id: UserId, tutorial_id: TutorialId) -> bool:
        """チュートリアル完了記録が存在するかチェック

        Args:
            user_id: ユーザーID
            tutorial_id: チュートリアルID

        Returns:
            bool: 完了記録が存在する場合 True
        """
        ...

    def list_completed_by_user(self, user_id: UserId) -> list[TutorialCompletion]:
        """指定ユーザーの全完了記録を取得

        Args:
            user_id: ユーザーID

        Returns:
            list[TutorialCompletion]: 完了記録のリスト
        """
        ...