from __future__ import annotations

from minio import Minio

from app.application.profile.ports.profile_image_storage_port import (
    ProfileImageStoragePort,
    StoredProfileImage,
)
from app.domain.auth.value_objects import UserId
from app.domain.profile.value_objects import ProfileImageId
from app.settings import settings


class MinioProfileImageStorage(ProfileImageStoragePort):
    """
    MinIO を使ったプロフィール画像ストレージ実装。

    - オブジェクトキー: profiles/{user_id}/avatar
    """

    def __init__(self) -> None:
        self._client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )
        self._bucket = settings.MINIO_BUCKET_PROFILE_IMAGES

        # バケットがなければ作成
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    def save(
        self,
        user_id: UserId,
        content: bytes,
        content_type: str,
    ) -> StoredProfileImage:
        object_name = f"profiles/{user_id.value}/avatar"

        # MinIO にアップロード
        from io import BytesIO

        data = BytesIO(content)
        size = len(content)

        self._client.put_object(
            bucket_name=self._bucket,
            object_name=object_name,
            data=data,
            length=size,
            content_type=content_type,
        )

        image_id = ProfileImageId(object_name)

        # presigned URL 等が必要ならここで発行して返す
        # url = self._client.presigned_get_object(self._bucket, object_name)
        return StoredProfileImage(id=image_id, url=None)

    def delete(self, image_id: ProfileImageId) -> None:
        self._client.remove_object(self._bucket, image_id.value)
