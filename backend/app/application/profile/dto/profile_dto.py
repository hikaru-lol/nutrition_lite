from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from app.domain.profile.value_objects import Sex


@dataclass
class ProfileDTO:
    """
    UseCase から API 層などに返すためのプロフィール情報。
    """

    user_id: str
    sex: Sex
    birthdate: date
    height_cm: float
    weight_kg: float
    image_id: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class UpsertProfileInputDTO:
    """
    プロフィール作成 / 更新時の入力 DTO。

    - 画像は任意。
    - 画像なしで呼べばテキスト情報だけ更新する。
    """

    user_id: str
    sex: Sex
    birthdate: date
    height_cm: float
    weight_kg: float

    image_content: bytes | None = None
    image_content_type: str | None = None
