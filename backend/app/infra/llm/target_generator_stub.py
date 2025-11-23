from __future__ import annotations

from datetime import date

from app.application.target.ports.target_generator_port import (
    TargetGeneratorPort,
    TargetGenerationContext,
    TargetGenerationResult,
)
from app.domain.target.entities import TargetNutrient
from app.domain.target.value_objects import (
    GoalType,
    ActivityLevel,
    NutrientCode,
    NutrientAmount,
    NutrientSource,
)


class StubTargetGenerator(TargetGeneratorPort):
    """
    TargetGeneratorPort のスタブ実装。

    - ユーザーの体重・活動レベル・目標に基づいて、
      ざっくりとした 17 栄養素のターゲットを決める。
    - あくまで「開発・テスト用のダミー実装」であり、
      実際の栄養指導や医療的な根拠は持たない。
    """

    def generate(self, ctx: TargetGenerationContext) -> TargetGenerationResult:
        # ------------------------
        # 基本パラメータの決定
        # ------------------------
        # 体重が不明なら 60kg として計算
        weight_kg = ctx.weight_kg or 60.0

        # 活動レベルごとのざっくり係数
        activity_factor = {
            ActivityLevel.LOW: 1.2,
            ActivityLevel.NORMAL: 1.4,
            ActivityLevel.HIGH: 1.6,
        }[ctx.activity_level]

        # 目標タイプごとのざっくり係数
        goal_factor = {
            GoalType.WEIGHT_LOSS: 0.9,
            GoalType.MAINTAIN: 1.0,
            GoalType.WEIGHT_GAIN: 1.1,
            GoalType.HEALTH_IMPROVE: 1.0,
        }[ctx.goal_type]

        # 超ざっくりな「1日エネルギー消費」の目安 (kcal)
        # ※ ここは本当に stub 用の適当な数字
        base_kcal = 28.0 * weight_kg
        target_kcal = base_kcal * activity_factor * goal_factor

        # PFC の比率（かなり単純化）
        carb_ratio = 0.50
        protein_ratio = 0.20
        fat_ratio = 0.30

        carb_g = target_kcal * carb_ratio / 4.0
        protein_g = max(weight_kg * 1.6, target_kcal *
                        protein_ratio / 4.0)  # 1.6 g/kg を下限
        fat_g = target_kcal * fat_ratio / 9.0

        # ------------------------
        # 栄養素ごとのターゲット値
        # （単位や値はすべて「それっぽいダミー」）
        # ------------------------
        nutrient_values: dict[NutrientCode, NutrientAmount] = {
            # エネルギー源
            NutrientCode.CARBOHYDRATE: NutrientAmount(value=round(carb_g, 1), unit="g"),
            NutrientCode.PROTEIN: NutrientAmount(value=round(protein_g, 1), unit="g"),
            NutrientCode.FAT: NutrientAmount(value=round(fat_g, 1), unit="g"),

            # ビタミン（かなりざっくり）
            # 男性の目安に近い値
            NutrientCode.VITAMIN_A: NutrientAmount(900.0, "µg"),
            NutrientCode.VITAMIN_B_COMPLEX: NutrientAmount(50.0, "mg"),
            NutrientCode.VITAMIN_C: NutrientAmount(100.0, "mg"),
            NutrientCode.VITAMIN_D: NutrientAmount(20.0, "µg"),
            NutrientCode.VITAMIN_E: NutrientAmount(10.0, "mg"),
            NutrientCode.VITAMIN_K: NutrientAmount(150.0, "µg"),

            # ミネラル（これもざっくり）
            NutrientCode.CALCIUM: NutrientAmount(700.0, "mg"),
            NutrientCode.IRON: NutrientAmount(10.0, "mg"),
            NutrientCode.MAGNESIUM: NutrientAmount(300.0, "mg"),
            NutrientCode.ZINC: NutrientAmount(10.0, "mg"),
            NutrientCode.SODIUM: NutrientAmount(1500.0, "mg"),
            NutrientCode.POTASSIUM: NutrientAmount(2500.0, "mg"),

            # その他
            NutrientCode.FIBER: NutrientAmount(20.0, "g"),
            NutrientCode.WATER: NutrientAmount(2000.0, "ml"),
        }

        # すべての NutrientCode に対して TargetNutrient を作成
        nutrients: list[TargetNutrient] = []
        for code in NutrientCode:
            amount = nutrient_values.get(
                code,
                # 万が一 dict に抜けがあったときのフォールバック
                NutrientAmount(0.0, "g"),
            )
            nutrients.append(
                TargetNutrient(
                    code=code,
                    amount=amount,
                    # Stub なので source は常に "llm" 扱い（≒自動生成）
                    source=NutrientSource("llm"),
                )
            )

        # ------------------------
        # 説明文と免責
        # ------------------------
        rationale_lines = [
            "StubTargetGenerator による簡易ターゲットです。",
            f"- 体重: {weight_kg:.1f} kg",
            f"- 活動レベル: {ctx.activity_level.value}",
            f"- 目標タイプ: {ctx.goal_type.value}",
            f"- 推定エネルギー: 約 {int(target_kcal)} kcal/日",
            "",
            "PFC バランスはおおよそ Carbohydrate 50%, Protein 20%, Fat 30% を仮定しています。",
        ]
        llm_rationale = "\n".join(rationale_lines)

        disclaimer = (
            "この栄養ターゲットはアプリ開発用のダミー実装に基づくものであり、"
            "実際の医療的助言や栄養指導を置き換えるものではありません。"
        )

        return TargetGenerationResult(
            nutrients=nutrients,
            llm_rationale=llm_rationale,
            disclaimer=disclaimer,
        )
