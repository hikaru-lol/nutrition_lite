from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from app.domain.profile.value_objects import Sex


# === Core DTO ===============================================================


@dataclass
class ProfileDTO:
    """
    UseCase から API 層などに返すためのプロフィール情報。

    - Sex はドメインの ValueObject をそのまま保持
    - height_cm / weight_kg は数値（単位付き）
    """

    user_id: str
    sex: Sex
    birthdate: date
    height_cm: float
    weight_kg: float
    image_id: str | None
    created_at: datetime
    updated_at: datetime
    meals_per_day: int | None = None


# === Input DTO (UseCase 入力) ===============================================


@dataclass
class UpsertProfileInputDTO:
    """
    プロフィール作成 / 更新時の入力 DTO。

    - 画像は任意（image_content / image_content_type）
    - 画像なしで呼べばテキスト情報だけ更新する
    """

    user_id: str
    sex: Sex
    birthdate: date
    height_cm: float
    weight_kg: float

    image_content: bytes | None = None
    image_content_type: str | None = None
    meals_per_day: int | None = None


# === Output DTO (用途が絞られたレスポンス用など) ============================


@dataclass
class ProfileOutputDTO:
    """
    プロフィール情報の一部だけを返したいときの簡易 DTO。

    - sex は文字列（例: "male" / "female" / "other"）
    - height / weight は数値（単位は呼び出し側の文脈に依存）
    """

    sex: str
    birthdate: date
    height: float
    weight: float
    image_id: str | None
    meals_per_day: int | None
