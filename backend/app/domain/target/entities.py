from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from app.domain.auth.value_objects import UserId
from app.domain.target.value_objects import (
    TargetId,
    GoalType,
    ActivityLevel,
    NutrientCode,
    NutrientSource,
    NutrientAmount,
)


@dataclass
class TargetNutrient:
    """
    1つの栄養素に対するターゲット値。

    - code   : 栄養素コード（carbohydrate, protein など）
    - amount : 目標量 + 単位（g / mg / µg / kcal など）
    - source : この値が LLM 由来か、手動編集かなど
    """

    code: NutrientCode
    amount: NutrientAmount
    source: NutrientSource


@dataclass
class TargetDefinition:
    """
    1日の栄養ターゲット定義。

    - プロフィール情報 + 目標情報を元に 17 栄養素の目標値を決定したもの。
    - ユーザーは複数のターゲットを持てるが、アクティブなのは常に1つだけ。
    """

    id: TargetId
    user_id: UserId

    title: str
    goal_type: GoalType
    goal_description: str | None
    activity_level: ActivityLevel

    # 1日あたりのターゲット栄養素セット（常に 17 要素を想定）
    nutrients: list[TargetNutrient]

    is_active: bool

    created_at: datetime
    updated_at: datetime

    # LLM がどういう根拠で出したかの説明
    llm_rationale: str | None = None

    # 医療行為ではない等の注意書き
    disclaimer: str | None = None

    def set_active(self) -> None:
        """このターゲットをアクティブ化する。"""
        self.is_active = True

    def set_inactive(self) -> None:
        """このターゲットを非アクティブにする。"""
        self.is_active = False

    def update_timestamp(self, now: datetime) -> None:
        """更新時に updated_at を現在時刻で更新する。"""
        self.updated_at = now

    def ensure_full_nutrients(self) -> None:
        """
        nutrients が 17 種のコードをすべてカバーしているか、
        必要ならここでチェックすることもできる。

        （実際のチェックロジックは後で必要になれば実装する）
        """
        # TODO: 必要なら実装
        pass


@dataclass
class DailyTargetSnapshot:
    """
    特定日付に対するターゲット値のスナップショット。

    - 過去日のみ作成し、以後変更しない（immutable）ことを想定。
    - 日付 D について、Active なターゲットからコピーして生成される。
    """

    user_id: UserId
    date: date
    target_id: TargetId

    # スナップショット時点の栄養ターゲット（17要素）
    nutrients: list[TargetNutrient]

    created_at: datetime
