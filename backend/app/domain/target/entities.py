from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Iterable

# === Domain (ValueObjects) ===================================================

from app.domain.auth.value_objects import UserId
from app.domain.target.value_objects import (
    TargetId,
    GoalType,
    ActivityLevel,
    NutrientCode,
    NutrientAmount,
    NutrientSource,
)


# === Domain Entities =========================================================


@dataclass
class TargetNutrient:
    """
    1つの栄養素に対するターゲット値。

    Attributes:
        code:
            栄養素コード（carbohydrate, protein など）。
        amount:
            目標量 + 単位（g / mg / µg / kcal など）。
        source:
            この値の由来（LLM 由来 / 手動編集など）。
    """

    code: NutrientCode
    amount: NutrientAmount
    source: NutrientSource


@dataclass
class TargetDefinition:
    """
    1日の栄養ターゲット定義。

    - プロフィール情報 + 目標情報を元に 17 栄養素の目標値を決定したもの。
    - ユーザーは複数のターゲットを持てるが、アクティブなのは常に 1 つだけ。
    """

    id: TargetId
    user_id: UserId

    title: str
    goal_type: GoalType
    goal_description: str | None
    activity_level: ActivityLevel

    # 1 日あたりのターゲット栄養素セット（常に 17 要素を想定）
    nutrients: list[TargetNutrient]

    is_active: bool

    created_at: datetime
    updated_at: datetime

    # LLM がどういう根拠で出したかの説明（任意）
    llm_rationale: str | None = None

    # 医療行為ではない等の注意書き（任意）
    disclaimer: str | None = None

    # --- ステート遷移系メソッド ------------------------------------

    def set_active(self) -> None:
        """このターゲットをアクティブ化する。"""
        self.is_active = True

    def set_inactive(self) -> None:
        """このターゲットを非アクティブにする。"""
        self.is_active = False

    def update_timestamp(self, now: datetime | None = None) -> None:
        """
        更新時に updated_at を現在時刻（UTC）で更新する。

        Args:
            now:
                テスト等で任意の時刻を指定したい場合に使用。
                None の場合は datetime.now(timezone.utc) を用いる。
        """
        if now is None:
            now = datetime.now(timezone.utc)
        self.updated_at = now

    # --- 栄養素関連のヘルパー --------------------------------------

    def get_nutrient(self, code: NutrientCode) -> TargetNutrient | None:
        """
        指定した栄養素コードに対応する TargetNutrient を返す。

        見つからない場合は None を返す。
        """
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

        - amount が None の場合は量は変更しない。
        - source が None の場合は由来は変更しない。

        Raises:
            ValueError:
                指定したコードの栄養素が存在しない場合。
                （必要に応じてドメイン専用エラーに差し替え可能）
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
        nutrients が必要な栄養素コードをすべてカバーしているかをチェックする。

        Args:
            required_codes:
                必須とみなす栄養素コードの集合。
                None の場合は NutrientCode の全列挙値を使用する。

        Raises:
            ValueError:
                必須コードが足りない場合。
                （実際にどこで呼ぶかはユースケース次第）
        """
        if required_codes is None:
            required_codes = list(NutrientCode)

        present = {n.code for n in self.nutrients}
        missing = [code for code in required_codes if code not in present]

        if missing:
            codes_str = ", ".join(c.value for c in missing)
            raise ValueError(
                f"Missing nutrient codes in TargetDefinition: {codes_str}"
            )


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

    # スナップショット時点の栄養ターゲット（17 要素）
    nutrients: tuple[TargetNutrient, ...]
    created_at: datetime

    # --- ファクトリーメソッド ---------------------------------------

    @classmethod
    def from_target(
        cls,
        target: TargetDefinition,
        snapshot_date: date,
        created_at: datetime | None = None,
    ) -> DailyTargetSnapshot:
        """
        Active な TargetDefinition から、その日付のスナップショットを作成する。

        - TargetNutrient 自体は新しくコピーを作成することで、
          後から TargetDefinition 側を変更してもスナップショット側が変わらないようにする。

        Args:
            target:
                スナップショット元となるターゲット定義。
            snapshot_date:
                スナップショット対象の日付。
            created_at:
                スナップショット作成時刻。None の場合は現在時刻（UTC）。

        Returns:
            DailyTargetSnapshot:
                指定日付・指定ターゲットに対応するスナップショット。
        """
        if created_at is None:
            created_at = datetime.now(timezone.utc)

        nutrients_copy = tuple(
            TargetNutrient(
                code=n.code,
                amount=n.amount,   # NutrientAmount は immutable 想定
                source=n.source,   # NutrientSource も immutable 想定
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
