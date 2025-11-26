from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Iterable
from uuid import UUID, uuid4

from app.domain.auth.value_objects import UserId
from app.domain.target.value_objects import (
    NutrientCode,
    NutrientAmount,
    NutrientSource,
)


@dataclass(frozen=True)
class DailyNutritionSummaryId:
    """
    DailyNutritionSummary の ID（UUID をラップした ValueObject）。
    """

    value: UUID

    @classmethod
    def new(cls) -> DailyNutritionSummaryId:
        return cls(uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class DailyNutrientIntake:
    """
    1日分の中の、ある1栄養素の摂取量。

    例:
      - code: NutrientCode.PROTEIN
      - amount: NutrientAmount(value=100.0, unit="g")
      - source: NutrientSource("llm")
    """

    code: NutrientCode
    amount: NutrientAmount
    source: NutrientSource


@dataclass
class DailyNutritionSummary:
    """
    1日分の栄養サマリのエンティティ。

    - id       : このサマリ自身の ID
    - user_id  : どのユーザーのサマリか
    - date     : 対象日
    - nutrients: その日1日分で摂取した栄養素ごとの一覧
    - generated_at: このサマリを計算した日時

    論理的には (user_id, date) で 1 レコード。
    """

    id: DailyNutritionSummaryId
    user_id: UserId
    date: date
    nutrients: list[DailyNutrientIntake] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        # code が重複しないようにチェック
        codes = [n.code for n in self.nutrients]
        if len(codes) != len(set(codes)):
            duplicated = [c for c in set(codes) if codes.count(c) > 1]
            raise ValueError(
                f"DailyNutritionSummary.nutrients has duplicated codes: {duplicated}"
            )

    # --- ユーティリティ -------------------------------------------------

    def get_amount(self, code: NutrientCode) -> NutrientAmount | None:
        """
        指定した栄養素コードの摂取量を取得する。存在しない場合は None。
        """
        for n in self.nutrients:
            if n.code == code:
                return n.amount
        return None

    def as_dict(self) -> dict:
        """
        後で API レスポンスやログ出力などに使える軽い helper。
        """
        return {
            "id": str(self.id.value),
            "user_id": self.user_id.value,
            "date": self.date.isoformat(),
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
        nutrients: Iterable[tuple[NutrientCode, NutrientAmount]],
        source: NutrientSource,
        summary_id: DailyNutritionSummaryId | None = None,
    ) -> DailyNutritionSummary:
        """
        (NutrientCode, NutrientAmount) のペア一覧から DailyNutritionSummary を生成する helper。

        - user_id, date: このサマリが表す 1 日
        - nutrients: code ごとの合計値（すでに集計済み）
        - source: その値の由来（例: NutrientSource("llm")）
        - summary_id:
            既存サマリを上書きしたい場合は既存 ID を渡す。
            新規作成の場合は None とし、新しい ID を採番する。
        """
        ints = [
            DailyNutrientIntake(code=code, amount=amount, source=source)
            for code, amount in nutrients
        ]

        return cls(
            id=summary_id or DailyNutritionSummaryId.new(),
            user_id=user_id,
            date=date,
            nutrients=ints,
            generated_at=datetime.utcnow(),
        )
