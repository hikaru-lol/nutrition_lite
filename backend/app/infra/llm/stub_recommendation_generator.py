from __future__ import annotations

from app.application.nutrition.dto.meal_recommendation_llm_dto import (
    MealRecommendationLLMInput,
    MealRecommendationLLMOutput,
    RecommendedMealDTO,
)
from app.application.nutrition.ports.recommendation_generator_port import (
    MealRecommendationGeneratorPort,
)


class StubMealRecommendationGenerator(MealRecommendationGeneratorPort):
    """
    開発・テスト用のスタブ実装。

    - recent_reports を軽く見てテキストをでっちあげるだけ。
    """

    def generate(self, input: MealRecommendationLLMInput) -> MealRecommendationLLMOutput:
        # base_date が文字列の場合と date オブジェクトの場合を両方サポート
        base_date_str = input.base_date if isinstance(input.base_date, str) else input.base_date.isoformat()
        days = len(input.recent_reports)

        body = (
            f"直近 {days} 日分（〜{base_date_str}）の食事傾向をもとに、"
            "次の食事の方針を簡単にまとめました。"
        )
        tips = [
            "毎食ごとにたんぱく質源（肉・魚・卵・大豆製品など）を 1 品入れてみましょう。",
            "野菜・海藻・きのこを 1 日 2 回以上は意識して取り入れてみてください。",
            "甘い飲み物やお菓子をとる場合は、時間帯や頻度を決めてメリハリをつけましょう。",
        ]

        # スタブ用の推奨献立3品
        recommended_meals = [
            RecommendedMealDTO(
                title="高タンパク朝食セット",
                description="卵とアボカドでタンパク質と良質な脂質をバランス良く摂取",
                ingredients=["卵2個", "アボカド1/2個", "全粒粉パン1枚", "トマト"],
                nutrition_focus="タンパク質20g摂取、食物繊維豊富"
            ),
            RecommendedMealDTO(
                title="野菜たっぷりランチ",
                description="鶏肉と季節野菜でバランスの取れた昼食",
                ingredients=["鶏むね肉100g", "ブロッコリー", "にんじん", "玄米ご飯"],
                nutrition_focus="低脂質高タンパク質、ビタミン豊富"
            ),
            RecommendedMealDTO(
                title="魚と野菜の夕食",
                description="魚を中心とした栄養バランス重視の夕食メニュー",
                ingredients=["鮭80g", "ほうれん草", "しめじ", "味噌汁"],
                nutrition_focus="オメガ3脂肪酸、鉄分補給"
            )
        ]

        return MealRecommendationLLMOutput(
            body=body,
            tips=tips,
            recommended_meals=recommended_meals,
        )
