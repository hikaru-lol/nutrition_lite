from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from app.domain.auth.value_objects import UserId
from app.domain.profile.value_objects import Sex, HeightCm, WeightKg, ProfileImageId


@dataclass
class Profile:
    """
    ユーザーの基本プロフィール情報。

    - User と 1:1 で紐づく（user_id）
    - ターゲット生成などに必要な「追加情報」は profile ではなく target 側で扱う方針。
    """

    user_id: UserId

    sex: Sex
    birthdate: date
    height_cm: HeightCm
    weight_kg: WeightKg

    # 任意のプロフィール画像（無ければ None）
    image_id: ProfileImageId | None

    meals_per_day: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def age(self) -> int:
        """
        本日時点のおおまかな年齢を返す。
        （将来、誤差が問題になる場合はアプリ側で別途扱う）
        """
        today = date.today()
        years = today.year - self.birthdate.year
        # 誕生日がまだ来ていなければ 1 歳引く
        if (today.month, today.day) < (self.birthdate.month, self.birthdate.day):
            years -= 1
        return years
