from __future__ import annotations

from typing import Optional

from app.application.target.ports.target_generator_port import (
    TargetGeneratorPort,
    GeneratedTargetNutrients,
)
from app.domain.profile.entities import Profile
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
    開発・テスト用のターゲット生成スタブ。

    - プロフィール / 目標情報を受け取るが、実際には単純な固定 or 簡易ロジックで
      17 栄養素ぶんの TargetNutrient を返す。
    - 本番では OpenAI などを使った実装に差し替える。
    """

    def generate(
        self,
        profile: Profile,
        goal_type: GoalType,
        activity_level: ActivityLevel,
        goal_description: Optional[str],
    ) -> GeneratedTargetNutrients:
        # 超ざっくりな例: goal_type / activity_level によって値を少し変える
        # 実際にはもっとちゃんとしたロジック or LLM に差し替える前提。
        base_kcal = 2000.0
        if goal_type == GoalType.WEIGHT_LOSS:
            base_kcal -= 300.0
        elif goal_type == GoalType.WEIGHT_GAIN:
            base_kcal += 300.0

        if activity_level == ActivityLevel.HIGH:
            base_kcal += 200.0
        elif activity_level == ActivityLevel.LOW:
            base_kcal -= 200.0

        # ざっくり PFC バランス
        protein = max(profile.weight_kg.value * 1.6, 60.0)   # 体重×1.6g or 60g
        fat = 0.25 * base_kcal / 9.0
        carb = (base_kcal - (protein * 4.0 + fat * 9.0)) / 4.0

        nutrients: list[TargetNutrient] = [
            TargetNutrient(
                code=NutrientCode.CARBOHYDRATE,
                amount=NutrientAmount(value=carb, unit="g"),
                source=NutrientSource("llm"),
            ),
            TargetNutrient(
                code=NutrientCode.FAT,
                amount=NutrientAmount(value=fat, unit="g"),
                source=NutrientSource("llm"),
            ),
            TargetNutrient(
                code=NutrientCode.PROTEIN,
                amount=NutrientAmount(value=protein, unit="g"),
                source=NutrientSource("llm"),
            ),
            # 他の栄養素は、とりあえず固定値を入れておく（後でチューニング可能）
            TargetNutrient(
                code=NutrientCode.VITAMIN_A,
                amount=NutrientAmount(value=700.0, unit="µg"),
                source=NutrientSource("llm"),
            ),
            TargetNutrient(
                code=NutrientCode.VITAMIN_B_COMPLEX,
                amount=NutrientAmount(value=100.0, unit="mg"),
                source=NutrientSource("llm"),
            ),
            TargetNutrient(
                code=NutrientCode.VITAMIN_C,
                amount=NutrientAmount(value=100.0, unit="mg"),
                source=NutrientSource("llm"),
            ),
            TargetNutrient(
                code=NutrientCode.VITAMIN_D,
                amount=NutrientAmount(value=20.0, unit="µg"),
                source=NutrientSource("llm"),
            ),
            TargetNutrient(
                code=NutrientCode.VITAMIN_E,
                amount=NutrientAmount(value=8.0, unit="mg"),
                source=NutrientSource("llm"),
            ),
            TargetNutrient(
                code=NutrientCode.VITAMIN_K,
                amount=NutrientAmount(value=150.0, unit="µg"),
                source=NutrientSource("llm"),
            ),
            TargetNutrient(
                code=NutrientCode.CALCIUM,
                amount=NutrientAmount(value=650.0, unit="mg"),
                source=NutrientSource("llm"),
            ),
            TargetNutrient(
                code=NutrientCode.IRON,
                amount=NutrientAmount(value=7.0, unit="mg"),
                source=NutrientSource("llm"),
            ),
            TargetNutrient(
                code=NutrientCode.MAGNESIUM,
                amount=NutrientAmount(value=300.0, unit="mg"),
                source=NutrientSource("llm"),
            ),
            TargetNutrient(
                code=NutrientCode.ZINC,
                amount=NutrientAmount(value=10.0, unit="mg"),
                source=NutrientSource("llm"),
            ),
            TargetNutrient(
                code=NutrientCode.SODIUM,
                amount=NutrientAmount(value=2000.0, unit="mg"),
                source=NutrientSource("llm"),
            ),
            TargetNutrient(
                code=NutrientCode.POTASSIUM,
                amount=NutrientAmount(value=2500.0, unit="mg"),
                source=NutrientSource("llm"),
            ),
            TargetNutrient(
                code=NutrientCode.FIBER,
                amount=NutrientAmount(value=20.0, unit="g"),
                source=NutrientSource("llm"),
            ),
            TargetNutrient(
                code=NutrientCode.WATER,
                amount=NutrientAmount(value=2000.0, unit="ml"),
                source=NutrientSource("llm"),
            ),
        ]

        rationale = (
            "This is a stubbed target generated based on goal_type and activity_level. "
            "In production, this would be generated by a more sophisticated model or LLM."
        )
        disclaimer = "This is not medical advice. Please consult a healthcare professional for personalized guidance."

        return GeneratedTargetNutrients(
            nutrients=nutrients,
            rationale=rationale,
            disclaimer=disclaimer,
        )
