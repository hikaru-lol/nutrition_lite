from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Optional

from app.domain.profile.entities import Profile
from app.domain.target.entities import TargetNutrient
from app.domain.target.value_objects import GoalType, ActivityLevel


@dataclass
class GeneratedTargetNutrients:
    """
    LLM / ルールベースなロジックにより生成されたターゲット栄養情報。

    - nutrients  : 17個の TargetNutrient（コード + amount + unit + source）
    - rationale  : どういう根拠でこの値になったか（説明文）
    - disclaimer : 医療行為ではない等の注意書き
    """

    nutrients: list[TargetNutrient]
    rationale: Optional[str] = None
    disclaimer: Optional[str] = None


class TargetGeneratorPort(Protocol):
    """
    プロフィール情報 + 目標情報から 17 種の栄養ターゲットを生成するポート。

    新規ターゲット作成時のみ利用し、
    既存ターゲットの編集時には使用しない（手動編集のみ）。
    """

    def generate(
        self,
        profile: Profile,
        goal_type: GoalType,
        activity_level: ActivityLevel,
        goal_description: Optional[str],
    ) -> GeneratedTargetNutrients:
        ...
