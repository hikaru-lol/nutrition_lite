from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.domain.auth.value_objects import UserId
from app.domain.profile.value_objects import ProfileImageId


@dataclass
class StoredProfileImage:
    """
    ストレージに保存されたプロフィール画像の情報。

    - id: ストレージ側のID（オブジェクトキー等）
    - url: フロントからアクセスするためのURL（必要であれば）
    """

    id: ProfileImageId
    url: str | None = None


class ProfileImageStoragePort(Protocol):
    """
    プロフィール画像の保存 / 削除を抽象化するポート。
    """

    def save(
        self,
        user_id: UserId,
        content: bytes,
        content_type: str,
    ) -> StoredProfileImage:
        """
        新しい画像を保存して StoredProfileImage を返す。
        既存画像の上書きにするか、別IDで保存するかは実装次第。
        """
        ...

    def delete(self, image_id: ProfileImageId) -> None:
        """
        指定したプロフィール画像を削除する。
        （後で画像差し替え時のクリーンアップなどで利用）
        """
        ...
