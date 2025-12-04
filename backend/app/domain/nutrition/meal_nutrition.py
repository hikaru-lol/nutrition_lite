from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Iterable
from uuid import UUID, uuid4

from app.domain.auth.value_objects import UserId
from app.domain.meal.value_objects import MealType
from app.domain.target.value_objects import (
    NutrientCode,
    NutrientAmount,
    NutrientSource,
    ALL_NUTRIENT_CODES,
)


@dataclass(frozen=True)
class MealNutritionSummaryId:
    """
    MealNutritionSummary の ID（UUID をラップした ValueObject）。
    """

    value: UUID

    @classmethod
    def new(cls) -> MealNutritionSummaryId:
        return cls(uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class MealNutrientIntake:
    """
    1食分の中の、ある1栄養素の摂取量。

    例:
      - code: NutrientCode.PROTEIN
      - amount: NutrientAmount(value=25.0, unit="g")
      - source: NutrientSource("llm")
    """

    code: NutrientCode
    amount: NutrientAmount
    source: NutrientSource


@dataclass
class MealNutritionSummary:
    """
    1回の食事に対する栄養サマリのエンティティ。

    - id: このサマリ自体のID（DBの主キーと対応）
    - user_id: どのユーザーの食事か
    - date: 食事の日付
    - meal_type: "main" or "snack"
    - meal_index:
        - meal_type == MAIN のとき: 1..N（何回目のメイン）
        - meal_type == SNACK のとき: None（間食は回数で区別しない）
    - nutrients: この食事で摂取した栄養素ごとの一覧
    - generated_at: このサマリをいつ計算したか
    """

    id: MealNutritionSummaryId
    user_id: UserId
    date: date
    meal_type: MealType
    meal_index: int | None
    nutrients: list[MealNutrientIntake] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        # code が重複しないように一応チェックだけしておく
        codes = [n.code for n in self.nutrients]
        if len(codes) != len(set(codes)):
            duplicated = [c for c in set(codes) if codes.count(c) > 1]
            raise ValueError(
                f"MealNutritionSummary.nutrients has duplicated codes: {duplicated}"
            )

        # MAIN のときは meal_index が 1 以上
        if self.meal_type == MealType.MAIN:
            if self.meal_index is None or self.meal_index < 1:
                raise ValueError(
                    f"MealType=MAIN の場合、meal_index は 1 以上の整数が必要です: {self.meal_index}"
                )
        # SNACK のときは meal_index は None
        elif self.meal_type == MealType.SNACK:
            if self.meal_index is not None:
                raise ValueError(
                    f"MealType=SNACK の場合、meal_index は None である必要があります: {self.meal_index}"
                )

    def ensure_full_nutrients(self) -> None:
        """
        この食事の栄養情報が、必要な 10 栄養素をすべて含んでいるかチェックする。

        - LLM / Estimator の実装ミス検出用。
        """
        present = {n.code for n in self.nutrients}
        missing = [code for code in ALL_NUTRIENT_CODES if code not in present]
        if missing:
            raise ValueError(
                "MealNutritionSummary is missing nutrients: "
                + ", ".join(m.value for m in missing)
            )

    # --- ユーティリティ -------------------------------------------------

    def get_amount(self, code: NutrientCode) -> NutrientAmount | None:
        """
        指定した栄養素コードの摂取量を取得する。
        存在しない場合は None。
        """
        for n in self.nutrients:
            if n.code == code:
                return n.amount
        return None

    def as_dict(self) -> dict:
        """
        後で API レスポンス用 DTO を組み立てるときなどに使える軽い helper。
        """
        return {
            "id": str(self.id.value),
            "user_id": self.user_id.value,
            "date": self.date.isoformat(),
            "meal_type": self.meal_type.value,
            "meal_index": self.meal_index,
            "generated_at": self.generated_at.isoformat(),
            "nutrients": [
                {
                    "code": n.code.value,
                    "amount": {
                        "value": n.amount.value,
                        "unit": n.amount.unit,
                    },
                    "source": n.source.value,
                }
                for n in self.nutrients
            ],
        }

    @classmethod
    def from_nutrient_amounts(
        cls,
        *,
        user_id: UserId,
        date: date,
        meal_type: MealType,
        meal_index: int | None,
        nutrients: Iterable[tuple[NutrientCode, NutrientAmount]],
        source: NutrientSource,
        summary_id: MealNutritionSummaryId | None = None,
    ) -> MealNutritionSummary:
        """
        Estimator の結果が (code, NutrientAmount) のペアで返ってくる場合に、
        まとめて MealNutritionSummary を作るための helper。

        summary_id が指定されていない場合は新しい ID を採番する。
        既存レコードの再計算などで既存 ID を維持したい場合は summary_id を渡す。
        """
        ints = [
            MealNutrientIntake(code=code, amount=amount, source=source)
            for code, amount in nutrients
        ]

        return cls(
            id=summary_id or MealNutritionSummaryId.new(),
            user_id=user_id,
            date=date,
            meal_type=meal_type,
            meal_index=meal_index,
            nutrients=ints,
            generated_at=datetime.utcnow(),
        )
