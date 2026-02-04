from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date as DateType
from typing import Any

from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field, ValidationError
from openai.types.chat import ParsedChatCompletion

from app.application.nutrition.dto.meal_recommendation_llm_dto import (
    MealRecommendationLLMInput,
    MealRecommendationLLMOutput,
    RecommendedMealDTO,
)
from app.application.nutrition.ports.recommendation_generator_port import (
    MealRecommendationGeneratorPort,
)
from app.domain.nutrition.errors import NutritionDomainError

logger = logging.getLogger(__name__)


class MealRecommendationGenerationFailedError(NutritionDomainError):
    """食事提案生成が失敗した場合のエラー。"""


# ------------------------------------------------------------------
# Structured Outputs用のレスポンススキーマ
# ------------------------------------------------------------------
class RecommendedMeal(BaseModel):
    """推奨される具体的な献立"""
    title: str = Field(
        description="献立名。例：「高タンパク朝食セット」「野菜たっぷりランチ」",
        min_length=5,
        max_length=30,
    )
    description: str = Field(
        description="献立の詳細説明と栄養価の特徴。50-100文字程度",
        min_length=30,
        max_length=120,
    )
    ingredients: list[str] = Field(
        description="主要な食材・料理名のリスト。3-6項目程度",
        min_items=3,
        max_items=6,
    )
    nutrition_focus: str = Field(
        description="この献立の栄養的なメリット。例：「タンパク質25g摂取可能」",
        min_length=10,
        max_length=50,
    )


class MealRecommendationResponseSchema(BaseModel):
    """
    OpenAI Structured Outputsで使用する食事提案のスキーマ。

    各フィールドのdescriptionが実質的なLLMへの指示として機能する。
    """
    body: str = Field(
        description=(
            "ユーザーの栄養状況を分析し、今後数日間で意識すべき食事のポイントを"
            "200-400文字程度の日本語で記述。現状の良い点と改善点を含める。"
        ),
        min_length=50,
        max_length=500,
    )
    tips: list[str] = Field(
        description=(
            "実際に行動に移せる具体的なアドバイス。各項目は30文字程度の簡潔な文で、"
            "2-5個の項目を提案。例：「朝食にタンパク質を20g追加」など。"
        ),
        min_items=2,
        max_items=5,
    )
    recommended_meals: list[RecommendedMeal] = Field(
        description="今日食べるのにおすすめの具体的な献立3品。バランスを考慮して提案",
        min_items=3,
        max_items=3,
    )


@dataclass(slots=True, frozen=True)
class OpenAIMealRecommendationGeneratorConfig:
    """OpenAI食事提案生成の設定。"""
    model: str = "gpt-4o-mini"  # コスト効率重視、Structured Outputs対応
    temperature: float = 0.3    # 一貫性を重視して少し下げる
    max_retries: int = 2        # リトライ回数


class OpenAIMealRecommendationGenerator(MealRecommendationGeneratorPort):
    """
    OpenAI Structured Outputsを使用した食事提案生成器。

    - JSON parseエラーを回避
    - 型安全性の確保
    - 明確なプロンプト構造
    """

    def __init__(
        self,
        client: OpenAI | None = None,
        config: OpenAIMealRecommendationGeneratorConfig | None = None,
    ) -> None:
        self._client = client or OpenAI()
        self._config = config or OpenAIMealRecommendationGeneratorConfig()

    def generate(self, input: MealRecommendationLLMInput) -> MealRecommendationLLMOutput:
        """食事提案を生成する。"""
        try:
            user_prompt = self._build_user_prompt(input)
            system_prompt = self._build_system_prompt()

            completion: ParsedChatCompletion[MealRecommendationResponseSchema] = self._client.beta.chat.completions.parse(
                model=self._config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self._config.temperature,
                response_format=MealRecommendationResponseSchema,
                max_retries=self._config.max_retries,
            )

            parsed_response: MealRecommendationResponseSchema | None = completion.choices[
                0].message.parsed
            if parsed_response is None:
                raise MealRecommendationGenerationFailedError(
                    "OpenAI failed to generate structured response"
                )

            # Pydantic -> DTO 変換
            recommended_meals_dto = [
                RecommendedMealDTO(
                    title=meal.title,
                    description=meal.description,
                    ingredients=meal.ingredients,
                    nutrition_focus=meal.nutrition_focus,
                )
                for meal in parsed_response.recommended_meals
            ]

            return MealRecommendationLLMOutput(
                body=parsed_response.body,
                tips=parsed_response.tips,
                recommended_meals=recommended_meals_dto,
            )

        except OpenAIError as e:
            logger.error(
                "OpenAI API error during meal recommendation generation",
                extra={
                    "user_id": input.user_id.value,
                    "base_date": input.base_date.isoformat(),
                    "error": str(e),
                },
            )
            raise MealRecommendationGenerationFailedError(
                "OpenAI APIエラーにより食事提案の生成に失敗しました"
            ) from e

        except ValidationError as e:
            logger.error(
                "Response validation failed",
                extra={"validation_errors": e.errors()},
            )
            raise MealRecommendationGenerationFailedError(
                "生成された応答の形式が不正でした"
            ) from e

        except Exception as e:
            logger.exception(
                "Unexpected error during meal recommendation generation")
            raise MealRecommendationGenerationFailedError(
                "予期しないエラーが発生しました"
            ) from e

    def _build_system_prompt(self) -> str:
        """システムプロンプトを構築する。"""
        return """\
あなたは経験豊富な管理栄養士として、ユーザーの栄養改善をサポートします。

## あなたの役割
- ユーザーの直近の食事記録と栄養状況を分析
- 実践的で継続可能な食事改善提案を行う
- 今日食べるべき具体的な献立を3品提案
- ユーザーのモチベーションを維持する励ましの言葉を添える

## 出力内容
1. **総合的なアドバイス**: 栄養状況の分析と改善方針
2. **実行可能なTips**: 具体的なアクション項目
3. **おすすめ献立3品**: 今日食べるのに最適な具体的な料理

## 献立提案の方針
- 入手しやすい食材を使用（コンビニ・スーパーで購入可能）
- 調理時間は30分以内を目安
- 栄養バランスを考慮（朝食・昼食・夕食 or 主食・主菜・副菜）
- ユーザーの改善点に直接対応
- 季節感のある食材を積極的に活用
- 日本人の食生活に馴染む料理を提案

## 制約事項
- 言語：日本語
- トーン：親しみやすく、専門的かつ実践的
- 医学的診断や治療に関する言及は避ける
- アレルギー情報がない場合は一般的な食材を使用
- 特殊な調理器具や高価な食材は避ける

## 分析観点
1. 栄養バランス（タンパク質、脂質、炭水化物）
2. 食事のタイミングと頻度
3. 改善の継続性と実現可能性
4. 既存の良い習慣の強化
"""

    def _build_user_prompt(self, input: MealRecommendationLLMInput) -> str:
        """ユーザー向けプロンプトを構築する。"""
        profile = input.profile
        reports = input.recent_reports

        sections = [
            f"## 分析対象日: {input.base_date.isoformat()}",
            "",
            "## ユーザー情報",
            f"- 性別: {self._format_sex(profile.sex or 'unknown')}",
            f"- 年齢: {self._calculate_age(profile.birthdate, input.base_date) if profile.birthdate else 'unknown'}歳",
            f"- 身長: {profile.height_cm or 'unknown'}cm",
            f"- 体重: {profile.weight_kg or 'unknown'}kg",
            f"- BMI: {self._calculate_bmi(profile.height_cm or 0, profile.weight_kg or 0):.1f}",
            f"- 1日の食事回数: {profile.meals_per_day}回",
            "",
            f"## 栄養レポート履歴（直近{len(reports)}日分）",
        ]

        if not reports:
            sections.append("※ 利用可能な栄養レポートがありません")
        else:
            for i, report in enumerate(reports, 1):
                sections.extend([
                    f"### {i}日前 ({report.date})",
                    f"**総合評価**: {report.summary}",
                ])

                if report.good_points:
                    sections.append(
                        f"**良い点**: {' / '.join(report.good_points)}")
                if report.improvement_points:
                    sections.append(
                        f"**改善点**: {' / '.join(report.improvement_points)}")
                if report.tomorrow_focus:
                    sections.append(
                        f"**注目ポイント**: {' / '.join(report.tomorrow_focus)}")
                sections.append("")

        sections.extend([
            "## 依頼",
            "上記の情報を踏まえて、今後数日間の食事で意識すべきポイントを提案してください。",
            "ユーザーが実際に行動に移せる、具体的で継続可能なアドバイスをお願いします。",
        ])

        return "\n".join(sections)

    # ------------------------------------------------------------------
    # ヘルパーメソッド
    # ------------------------------------------------------------------
    def _format_sex(self, sex: str) -> str:
        """性別を日本語で表示。"""
        mapping = {"male": "男性", "female": "女性", "other": "その他"}
        return mapping.get(sex.lower(), sex)

    def _calculate_age(self, birthdate: DateType, base_date: DateType) -> int:
        """年齢を計算。"""
        return base_date.year - birthdate.year - (
            (base_date.month, base_date.day) < (birthdate.month, birthdate.day)
        )

    def _calculate_bmi(self, height_cm: float, weight_kg: float) -> float:
        """BMIを計算。"""
        height_m = height_cm / 100
        return weight_kg / (height_m ** 2)
