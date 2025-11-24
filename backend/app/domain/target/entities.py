from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Iterable

from app.domain.auth.value_objects import UserId
from app.domain.target.value_objects import (
    TargetId,
    GoalType,
    ActivityLevel,
    NutrientCode,
    NutrientAmount,
    NutrientSource,
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

    # --- ステート遷移系メソッド ------------------------------------

    def set_active(self) -> None:
        """このターゲットをアクティブ化する。"""
        self.is_active = True

    def set_inactive(self) -> None:
        """このターゲットを非アクティブにする。"""
        self.is_active = False

    def update_timestamp(self, now: datetime | None = None) -> None:
        """更新時に updated_at を現在時刻で更新する。"""
        if now is None:
            now = datetime.now(timezone.utc)
        self.updated_at = now

    # --- 栄養素関連のヘルパー --------------------------------------

    def get_nutrient(self, code: NutrientCode) -> TargetNutrient | None:
        """指定した栄養素コードに対応する TargetNutrient を返す。"""
        for n in self.nutrients:
            if n.code == code:
                return n
        return None

    def update_nutrient(
        self,
        code: NutrientCode,
        amount: NutrientAmount | None = None,
        source: NutrientSource | None = None,
    ) -> None:
        """
        指定した栄養素の値を更新する。

        - amount が None の場合は量は変更しない
        - source が None の場合は由来は変更しない
        """
        nutrient = self.get_nutrient(code)
        if nutrient is None:
            raise ValueError(f"Unknown nutrient code: {code.value}")

        if amount is not None:
            nutrient.amount = amount

        if source is not None:
            nutrient.source = source

    def ensure_full_nutrients(
        self,
        required_codes: Iterable[NutrientCode] | None = None,
    ) -> None:
        """
        nutrients が 17 種のコードをすべてカバーしているかをチェックする。

        実際に呼び出すかどうかはユースケース次第。
        """
        if required_codes is None:
            required_codes = list(NutrientCode)

        present = {n.code for n in self.nutrients}
        missing = [code for code in required_codes if code not in present]
        if missing:
            codes_str = ", ".join(c.value for c in missing)
            raise ValueError(
                f"Missing nutrient codes in TargetDefinition: {codes_str}")


@dataclass(frozen=True)
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
    nutrients: tuple[TargetNutrient, ...]
    created_at: datetime

    @classmethod
    def from_target(
        cls,
        target: TargetDefinition,
        snapshot_date: date,
        created_at: datetime | None = None,
    ) -> DailyTargetSnapshot:
        """
        Active な TargetDefinition から、その日付のスナップショットを作成する。

        - TargetNutrient 自体は新しくコピーを作成することで、後から
          TargetDefinition 側を変更してもスナップショットが変わらないようにする。
        """
        if created_at is None:
            created_at = datetime.now(timezone.utc)

        nutrients_copy = tuple(
            TargetNutrient(
                code=n.code,
                amount=n.amount,      # NutrientAmount は immutable
                source=n.source,      # NutrientSource も immutable
            )
            for n in target.nutrients
        )

        return cls(
            user_id=target.user_id,
            date=snapshot_date,
            target_id=target.id,
            nutrients=nutrients_copy,
            created_at=created_at,
        )
