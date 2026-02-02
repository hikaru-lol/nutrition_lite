"""チュートリアルドメインの値オブジェクト"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import NewType

# 型エイリアス
TutorialId = NewType("TutorialId", str)
UserId = NewType("UserId", str)


@dataclass(frozen=True)
class TutorialCompletion:
    """チュートリアル完了記録 - 値オブジェクト

    レコードの存在 = 完了を表す不変な値オブジェクト
    """
    user_id: UserId
    tutorial_id: TutorialId
    completed_at: datetime

    @staticmethod
    def create(user_id: UserId, tutorial_id: TutorialId) -> TutorialCompletion:
        """新しい完了記録を作成"""
        from datetime import timezone

        return TutorialCompletion(
            user_id=user_id,
            tutorial_id=tutorial_id,
            completed_at=datetime.now(timezone.utc)
        )

    def is_completed_by_user(self, user_id: UserId) -> bool:
        """指定ユーザーによる完了かどうかを判定"""
        return self.user_id == user_id