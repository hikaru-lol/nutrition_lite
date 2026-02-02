"""チュートリアルドメインエラー"""

from __future__ import annotations


class TutorialError(Exception):
    """チュートリアル関連エラーの基底クラス"""
    pass


class InvalidTutorialIdError(TutorialError):
    """存在しないチュートリアルIDが指定された場合"""

    def __init__(self, tutorial_id: str):
        self.tutorial_id = tutorial_id
        super().__init__(f"Invalid tutorial ID: {tutorial_id}")


class TutorialAlreadyCompletedError(TutorialError):
    """既に完了済みのチュートリアルを再度完了しようとした場合"""

    def __init__(self, user_id: str, tutorial_id: str):
        self.user_id = user_id
        self.tutorial_id = tutorial_id
        super().__init__(
            f"Tutorial '{tutorial_id}' already completed by user '{user_id}'"
        )