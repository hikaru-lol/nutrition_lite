from __future__ import annotations


class LogoutUserUseCase:
    """
    現時点ではサーバ側でトークン管理をしていないため、No-Op。
    将来、リフレッシュトークンのブラックリストやセッションテーブルを
    導入する場合は、ここで無効化処理を行う。
    """

    def execute(self, user_id: str | None = None) -> None:
        # 何もしない
        return None
