from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.domain.profile.value_objects import Sex


class ProfileRequest(BaseModel):
    """
    プロフィール作成 / 更新用のリクエストボディ。

    画像は現時点では別エンドポイントで扱う前提。
    （後で multipart/form-data + UploadFile に拡張してもよい）
    """

    sex: Sex
    birthdate: date
    height_cm: float = Field(gt=0, lt=300)
    weight_kg: float = Field(gt=0, lt=500)

    meals_per_day: int | None = Field(
        default=None,
        ge=1,
        le=6,
        description="1日にメインの食事をとる回数（例: 2〜4）。省略可",
    )


class ProfileResponse(BaseModel):
    """
    プロフィール取得時のレスポンス。

    image_id はプロフィール画像のストレージ上の ID（オブジェクトキーなど）。
    """

    user_id: str
    sex: Sex
    birthdate: date
    height_cm: float
    weight_kg: float
    image_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    meals_per_day: int | None = Field(
        default=None,
        ge=1,
        le=6,
        description="1日にメインの食事をとる回数（例: 2〜4）。省略可",
    )
