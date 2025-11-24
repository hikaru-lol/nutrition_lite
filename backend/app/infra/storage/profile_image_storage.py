from __future__ import annotations

from typing import Dict

from app.application.profile.ports.profile_image_storage_port import (
    ProfileImageStoragePort,
    StoredProfileImage,
)
from app.domain.auth.value_objects import UserId
from app.domain.profile.value_objects import ProfileImageId


class InMemoryProfileImageStorage(ProfileImageStoragePort):
    """
    テスト・開発用の In-Memory プロフィール画像ストレージ実装。

    - 実際の環境では MinIO / S3 などの実装に置き換える前提。
    - プロセスが落ちるとデータは消える。
    """

    def __init__(self) -> None:
        # key: ProfileImageId.value, value: (bytes, content_type)
        self._store: Dict[str, tuple[bytes, str]] = {}

    def save(
        self,
        user_id: UserId,
        content: bytes,
        content_type: str,
    ) -> StoredProfileImage:
        # シンプルに user_id ベースのキーを使う（1ユーザー1画像想定）
        key = f"profile/{user_id.value}/avatar"

        # メモリ上に保存
        self._store[key] = (content, content_type)

        image_id = ProfileImageId(key)
        # URL は InMemory では意味がないので None。将来 MinIO 実装で presigned URL を返してもよい。
        return StoredProfileImage(id=image_id, url=None)

    def delete(self, image_id: ProfileImageId) -> None:
        self._store.pop(image_id.value, None)
