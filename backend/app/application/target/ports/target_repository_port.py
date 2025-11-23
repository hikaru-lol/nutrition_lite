from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.auth.value_objects import UserId
from app.domain.target.entities import TargetDefinition
from app.domain.target.value_objects import TargetId


@runtime_checkable
class TargetRepositoryPort(Protocol):
    """
    TargetDefinition を永続化するためのリポジトリポート。

    - Application 層からはこのインターフェイスだけを見る
    - 実装は infra/db/repositories/target_repository.py などで行う
    """

    # --- Create ---------------------------------------------------------

    def add(self, target: TargetDefinition) -> None:
        """
        新しい TargetDefinition を永続化する。

        - まだ id が採番されていない場合は、実装側で UUID などを採番してもよい
        """
        ...

    # --- Read -----------------------------------------------------------

    def get_by_id(self, user_id: UserId, target_id: TargetId) -> TargetDefinition | None:
        """
        user_id + target_id で 1件取得する。

        - ログインユーザーに属していない Target は None を返す（=アクセス不可）
        """
        ...

    def get_active(self, user_id: UserId) -> TargetDefinition | None:
        """
        現在 Active な TargetDefinition を 1件返す。

        - なければ None
        - ユーザーごとに Active は高々 1件であることが不変条件
        """
        ...

    def list_by_user(
        self,
        user_id: UserId,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[TargetDefinition]:
        """
        ユーザーに紐づく TargetDefinition の一覧を返す。

        - limit / offset でページング
        - 並び順は created_at DESC（新しい順）などを想定（実装側で決めてOK）
        """
        ...

    # --- Update ---------------------------------------------------------

    def save(self, target: TargetDefinition) -> None:
        """
        既存の TargetDefinition の状態を保存する。

        - SQLAlchemy 実装では、Session に attach 済みであれば no-op でもよい
        """
        ...

    def deactivate_all(self, user_id: UserId) -> None:
        """
        指定ユーザーの TargetDefinition の is_active を全て False にする。

        - ActivateTargetUseCase で使用する想定
        - パフォーマンスのために、UseCase から一括 UPDATE を許可している
        """
        ...
