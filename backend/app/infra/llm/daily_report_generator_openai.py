from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field

from app.application.nutrition.dto.daily_report_llm_dto import (
    DailyReportLLMInput,
    DailyReportLLMOutput,
)
from app.application.nutrition.ports.daily_report_generator_port import (
    DailyNutritionReportGeneratorPort,
)
from app.application.nutrition.errors import DailyReportGenerationFailedError
from app.domain.profile.entities import Profile
from app.domain.target.entities import DailyTargetSnapshot
from app.domain.nutrition.daily_nutrition import DailyNutritionSummary
from app.domain.nutrition.meal_nutrition import MealNutritionSummary

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# 1. 出力構造の定義 (Pydantic / Structured Outputs)
# ------------------------------------------------------------------
class DailyReportResponseSchema(BaseModel):
    summary: str = Field(
        ...,
        description="本日の食事内容全体の総評。200〜300文字程度の日本語で、ユーザーを労いながら概要を伝えてください。"
    )
    good_points: list[str] = Field(
        ...,
        description="本日の食事で良かった点（例：タンパク質が目標通り、野菜を摂取できた等）。箇条書き用リスト。"
    )
    improvement_points: list[str] = Field(
        ...,
        description="改善できる点や注意点（例：塩分が少し多め、脂質が不足気味等）。箇条書き用リスト。"
    )
    tomorrow_focus: list[str] = Field(
        ...,
        description="明日意識すべき具体的なアクション（例：朝食で卵を追加する、水分を多めに摂る等）。箇条書き用リスト。"
    )


# ------------------------------------------------------------------
# 2. システムプロンプト (日本語化・役割定義)
# ------------------------------------------------------------------
_SYSTEM_PROMPT = """\
あなたは管理栄養士・スポーツ栄養士の資格を持つ専属AI栄養トレーナーです。
ユーザーの本日の食事データと目標値に基づき、専門的な日次フィードバックレポートを作成してください。

【専門知識】
1. ボディメイク栄養学
   - 増量期：カロリー過剰+適切なPFCバランス（たんぱく質1.6-2.2g/kg、脂質20-35%、炭水化物残り）
   - 減量期：カロリー不足+筋肉維持（たんぱく質2.0-2.5g/kg、脂質15-25%、炭水化物調整）
   - 維持期：エネルギーバランス+栄養密度重視

2. PFCバランス最適化
   - たんぱく質：筋合成・回復の要（1食20-40g推奨）
   - 脂質：ホルモン産生・必須脂肪酸（不足は代謝低下）
   - 炭水化物：筋グリコーゲン・脳エネルギー（トレーニング強度に応じて調整）

3. 栄養タイミング
   - トレーニング前：炭水化物+少量たんぱく質（2-3時間前）
   - トレーニング後：たんぱく質+炭水化物（30分以内、ゴールデンタイム）
   - 就寝前：カゼインプロテインまたは消化の良いたんぱく質

4. マイクロ栄養素の重要性
   - ビタミンD：筋力・骨健康（不足率高い）
   - 鉄：酸素運搬（特に女性は注意）
   - 亜鉛：たんぱく質合成・回復
   - マグネシウム：筋収縮・エネルギー代謝

【出力指針】
1. 必ず具体的数値でフィードバック（例：「たんぱく質120g摂取で目標達成率105%、素晴らしい！」）
2. 改善提案は実行可能な3ステップで提示（優先度順）
3. 明日のアクションは具体的で実現しやすいものを（食材名・タイミング・分量含む）
4. good_pointsを必ず見つけて褒める（モチベーション維持最優先）
5. 科学的根拠に基づくアドバイス（但し医学的診断は避ける）

【言語・トーン】
- 日本語での出力必須
- 親しみやすく前向きなトーン
- 専門用語は適度に使用し、初心者にもわかりやすく説明
"""


@dataclass(slots=True)
class OpenAIDailyReportGeneratorConfig:
    model: str = "gpt-4o-mini"  # コスト効率的なモデル（95%コスト削減）
    temperature: float = 0.4


class OpenAIDailyNutritionReportGenerator(DailyNutritionReportGeneratorPort):
    """
    OpenAI Structured Outputs を使って日次栄養レポート文面を生成する実装。
    """

    def __init__(
        self,
        client: OpenAI | None = None,
        config: OpenAIDailyReportGeneratorConfig | None = None,
    ) -> None:
        self._client = client or OpenAI()
        self._config = config or OpenAIDailyReportGeneratorConfig()

    def _validate_input(self, input: DailyReportLLMInput) -> None:
        """入力データの妥当性を検証"""

        # 必須データの存在確認
        if not input.daily_summary.nutrients:
            raise DailyReportGenerationFailedError(
                "栄養データが記録されていません。食事を登録してからレポート生成を行ってください。"
            )

        if len(input.meal_summaries) == 0:
            raise DailyReportGenerationFailedError(
                "食事記録がありません。最低1食分の記録が必要です。"
            )

        # 重要栄養素の存在確認（OpenAPI仕様のPFCのみ、警告のみでエラーにはしない）
        essential_nutrients = ['protein', 'carbohydrate', 'fat']
        recorded_codes = {n.code.value for n in input.daily_summary.nutrients}
        missing_nutrients = [n for n in essential_nutrients if n not in recorded_codes]

        if missing_nutrients:
            logger.warning(
                f"重要な栄養素が不足しています: {missing_nutrients}, user_id={getattr(input.user_id, 'value', input.user_id)}"
            )

        # データの妥当性チェック
        for nutrient in input.daily_summary.nutrients:
            if nutrient.amount.value < 0:
                logger.warning(
                    f"負の栄養値が検出されました: {nutrient.code.value}={nutrient.amount.value}"
                )

        # プロフィール情報の基本チェック
        profile = input.profile
        height = getattr(profile, 'height_cm', None)
        weight = getattr(profile, 'weight_kg', None)

        if height and (height < 100 or height > 250):
            logger.warning(f"身長の値が異常です: {height}cm")

        if weight and (weight < 20 or weight > 300):
            logger.warning(f"体重の値が異常です: {weight}kg")

    def generate(self, input: DailyReportLLMInput) -> DailyReportLLMOutput:
        """
        LLM に日次レポート生成を依頼する。
        """
        # 入力検証を最初に実行
        self._validate_input(input)

        user_prompt = self._build_user_prompt(input)

        try:
            # ------------------------------------------------------------------
            # 3. リクエスト実行 (beta.parse を使用)
            # ------------------------------------------------------------------
            completion = self._client.beta.chat.completions.parse(
                model=self._config.model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self._config.temperature,
                response_format=DailyReportResponseSchema,
            )

            parsed_response = completion.choices[0].message.parsed

            if parsed_response is None:
                raise DailyReportGenerationFailedError(
                    "OpenAI refused to generate structured output."
                )

            # DTOへの詰め替え
            return DailyReportLLMOutput(
                summary=parsed_response.summary,
                good_points=parsed_response.good_points,
                improvement_points=parsed_response.improvement_points,
                tomorrow_focus=parsed_response.tomorrow_focus,
            )

        except OpenAIError as e:
            logger.exception(
                "OpenAI API error: user=%s date=%s",
                getattr(input.user_id, "value", input.user_id),
                input.date,
            )
            raise DailyReportGenerationFailedError(
                "Failed to generate daily nutrition report via OpenAI"
            ) from e
        except Exception as e:
            logger.exception("Unexpected error during daily report generation")
            raise DailyReportGenerationFailedError(
                "An unexpected error occurred"
            ) from e

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    def _translate_nutrient(self, code: str) -> str:
        """栄養素コードを日本語名に変換（OpenAPI仕様に準拠した10種類）"""
        translations = {
            # OpenAPI仕様準拠の10種類の栄養素のみ
            'carbohydrate': '炭水化物',
            'fat': '脂質',
            'protein': 'たんぱく質',
            'water': '水分',
            'fiber': '食物繊維',
            'sodium': 'ナトリウム',
            'iron': '鉄',
            'calcium': 'カルシウム',
            'vitamin_d': 'ビタミンD',
            'potassium': 'カリウム'
        }
        return translations.get(code, code.replace('_', ' ').title())

    def _get_status_emoji(self, percentage: float) -> str:
        """達成度に基づく絵文字ステータスを返す"""
        if percentage >= 95:
            return "🎯"  # 完璧達成
        elif percentage >= 80:
            return "✅"  # 良好
        elif percentage >= 60:
            return "📊"  # 進行中
        else:
            return "⚠️"  # 要改善

    def _build_nutrition_analysis(self, input: DailyReportLLMInput) -> str:
        """目標 vs 実績の詳細比較分析を生成"""
        daily = input.daily_summary
        target = input.target_snapshot

        lines = []
        lines.append("【目標達成度分析】")

        # 重要栄養素の優先表示（OpenAPI仕様のPFCのみ）
        priority_nutrients = ['protein', 'carbohydrate', 'fat']

        for code in priority_nutrients:
            actual = next((n for n in daily.nutrients if n.code.value == code), None)

            # target.nutrients から対応する栄養素を検索
            target_nutrient = None
            if hasattr(target, 'nutrients') and target.nutrients:
                target_nutrient = next((t for t in target.nutrients if t.code.value == code), None)

            if actual and target_nutrient:
                # TargetNutrient は amount 属性を直接持つ (value_objects.py参照)
                target_amount = target_nutrient.amount.value
                actual_amount = actual.amount.value
                percentage = (actual_amount / target_amount) * 100
                status_emoji = self._get_status_emoji(percentage)
                nutrient_name = self._translate_nutrient(code)

                lines.append(
                    f"{status_emoji} {nutrient_name}: "
                    f"{actual_amount:.1f}{actual.amount.unit} / "
                    f"{target_amount:.1f}{actual.amount.unit} "
                    f"({percentage:.0f}%)"
                )
            elif actual:
                # 目標値がない場合は実績値のみ表示
                nutrient_name = self._translate_nutrient(code)
                lines.append(f"📝 {nutrient_name}: {actual.amount.value:.1f}{actual.amount.unit}")

        # その他の栄養素
        other_nutrients = [n for n in daily.nutrients if n.code.value not in priority_nutrients]
        if other_nutrients:
            lines.append("")
            lines.append("【その他の栄養素】")
            for nutrient in other_nutrients[:6]:  # 最大6つまで表示
                nutrient_name = self._translate_nutrient(nutrient.code.value)
                lines.append(f"📝 {nutrient_name}: {nutrient.amount.value:.1f}{nutrient.amount.unit}")

        return "\n".join(lines)

    def _build_user_prompt(self, input: DailyReportLLMInput) -> str:
        """
        LLMに渡すテキストを構築。
        できるだけ「目標値 vs 実績値」の対比がわかるように渡すのがコツです。
        """

        profile: Profile = input.profile
        target: DailyTargetSnapshot = input.target_snapshot
        daily: DailyNutritionSummary = input.daily_summary
        meal_summaries: list[MealNutritionSummary] = list(input.meal_summaries)

        lines: list[str] = []

        # --- 基本情報 ---
        lines.append(f"【日付】: {input.date.isoformat()}")
        lines.append("")
        lines.append("【ユーザープロフィール】")
        # getattr安全策はそのまま維持しつつ日本語ラベル化
        sex = getattr(profile, 'sex', '不明')
        height = getattr(profile, 'height_cm', '不明')
        weight = getattr(profile, 'weight_kg', '不明')
        lines.append(f"- 性別: {sex}")
        lines.append(f"- 身長: {height} cm")
        lines.append(f"- 体重: {weight} kg")
        lines.append("")

        # --- 目標設定 ---
        lines.append("【本日の目標設定】")
        goal_type = getattr(target, 'goal_type', '不明')  # weight_gain 等
        lines.append(f"- 目的: {goal_type}")
        # もし target.targets (リスト) に具体的な数値が入っているなら、ここで展開すると良いです
        # 例:
        # lines.append("- 目標カロリー: 3000 kcal")
        lines.append("")

        # --- 詳細な栄養分析 ---
        nutrition_analysis = self._build_nutrition_analysis(input)
        lines.append(nutrition_analysis)
        lines.append("")

        # --- 食事ごとの内訳 ---
        lines.append("【食事ごとの記録】")
        if not meal_summaries:
            lines.append("（記録なし）")

        for idx, m in enumerate(meal_summaries, start=1):
            meal_type = getattr(m, 'meal_type', '不明')
            lines.append(f"▼ {idx}回目の食事 ({meal_type})")

            # 各食事で何を食べたか（料理名）がもし取れるならここに入れたいです
            # 現状の MealNutritionSummary に料理名リストがない場合は栄養素数だけ表示
            item_count = len(m.nutrients)
            lines.append(f"  - 栄養素データ数: {item_count}項目")

            # 各食事のカロリーなどがわかれば記載
            # for n in m.nutrients: ...

        lines.append("")
        lines.append(
            "以上のデータに基づき、ユーザーへの日次フィードバックレポート（日本語）を作成してください。"
        )

        return "\n".join(lines)
