from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import date as DateType
from typing import Any, Sequence

from openai import OpenAI, OpenAIError

from app.application.nutrition.ports.nutrition_estimator_port import (
    NutritionEstimatorPort,
)
from app.application.nutrition.dto.meal_nutrient_intake_dto import (
    MealNutrientIntake,
)
from app.domain.auth.value_objects import UserId
from app.domain.meal.entities import FoodEntry
from app.domain.nutrition.errors import NutritionEstimationFailedError
from app.domain.target.value_objects import (
    NutrientAmount,
    NutrientCode,
    NutrientSource,
)

logger = logging.getLogger(__name__)


# === LLM 用プロンプト =======================================================

_SYSTEM_PROMPT = """\
You are a registered dietitian and nutrition expert.

Your task:
Given a single meal (one eating occasion) with multiple food items,
estimate the nutrient intakes for that meal.

You MUST return a JSON object with the following structure:

{
  "nutrients": {
    "carbohydrate":  {"amount": <number>, "unit": "g"},
    "fat":           {"amount": <number>, "unit": "g"},
    "protein":       {"amount": <number>, "unit": "g"},
    "water":         {"amount": <number>, "unit": "ml"},
    "fiber":         {"amount": <number>, "unit": "g"},
    "sodium":        {"amount": <number>, "unit": "mg"},
    "iron":          {"amount": <number>, "unit": "mg"},
    "calcium":       {"amount": <number>, "unit": "mg"},
    "vitamin_d":     {"amount": <number>, "unit": "µg"},
    "potassium":     {"amount": <number>, "unit": "mg"}
  }
}

Requirements:

- "nutrients" must be an object whose keys are exactly these 10 nutrient codes.
- Do NOT omit any of the 10 codes above.
- Do NOT add any extra keys in "nutrients".
- Each nutrient object must have:
    - "amount": a numeric value
    - "unit": exactly the unit shown above for that nutrient
- Use realistic ranges for a single meal based on the described foods.
- If the same nutrient appears in multiple items, sum them up.
- If some information is missing, make reasonable assumptions.
- Do NOT include any extra keys outside this JSON object.
"""


# === 10栄養素セット & 単位定義 ==============================================

EXPECTED_CODES: list[NutrientCode] = [
    NutrientCode.CARBOHYDRATE,
    NutrientCode.FAT,
    NutrientCode.PROTEIN,
    NutrientCode.WATER,
    NutrientCode.FIBER,
    NutrientCode.SODIUM,
    NutrientCode.IRON,
    NutrientCode.CALCIUM,
    NutrientCode.VITAMIN_D,
    NutrientCode.POTASSIUM,
]

EXPECTED_UNITS: dict[NutrientCode, str] = {
    NutrientCode.CARBOHYDRATE: "g",
    NutrientCode.FAT: "g",
    NutrientCode.PROTEIN: "g",
    NutrientCode.WATER: "ml",
    NutrientCode.FIBER: "g",
    NutrientCode.SODIUM: "mg",
    NutrientCode.IRON: "mg",
    NutrientCode.CALCIUM: "mg",
    NutrientCode.VITAMIN_D: "µg",
    NutrientCode.POTASSIUM: "mg",
}


@dataclass(slots=True)
class OpenAINutritionEstimatorConfig:
    """
    OpenAI ベースの NutritionEstimator 用設定。

    - model: 使用するモデル名 (例: "gpt-4o-mini")
    - temperature: 出力の多様性
    """

    model: str = "gpt-4o-mini"
    temperature: float = 0.1
    # 必要に応じて max_tokens などを追加


class OpenAINutritionEstimator(NutritionEstimatorPort):
    """
    OpenAI Chat Completions API を使って Meal 単位の栄養素を推定する実装。

    - OPENAI_API_KEY は環境変数から読み込む前提。
    - JSON モードで nutrients を返させ、MealNutrientIntake にマッピングする。
    """

    def __init__(
        self,
        client: OpenAI | None = None,
        config: OpenAINutritionEstimatorConfig | None = None,
    ) -> None:
        self._client = client or OpenAI()
        self._config = config or OpenAINutritionEstimatorConfig()

    # ------------------------------------------------------------------
    # Port 実装
    # ------------------------------------------------------------------

    def estimate_for_entries(
        self,
        user_id: UserId,
        date: DateType,
        entries: Sequence[FoodEntry],
    ) -> list[MealNutrientIntake]:
        """
        指定ユーザー・日付・Meal の FoodEntry 群から栄養素を推定する。

        Raises:
            NutritionEstimationFailedError: 外部 API や JSON パースなどの失敗時
        """
        # Meal に紐づく FoodEntry が 0 件なら、栄養素 0 として扱うか空で返す。
        # ここでは空リストを返す（呼び出し側は「栄養なし」として扱う）。
        if not entries:
            logger.info(
                "No FoodEntry for user=%s date=%s; returning empty nutrient list",
                user_id.value,
                date,
            )
            return []

        user_prompt = self._build_user_prompt(user_id, date, entries)

        try:
            completion = self._client.chat.completions.create(
                model=self._config.model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self._config.temperature,
                response_format={"type": "json_object"},
            )
        except OpenAIError as e:
            logger.exception(
                "OpenAI API error while estimating nutrition: user=%s date=%s",
                user_id.value,
                date,
            )
            raise NutritionEstimationFailedError(
                "Failed to estimate nutrition via OpenAI"
            ) from e

        content = completion.choices[0].message.content
        if content is None:
            raise NutritionEstimationFailedError(
                "OpenAI returned empty content"
            )

        try:
            data: dict[str, Any] = json.loads(content)
        except json.JSONDecodeError:
            logger.exception(
                "Failed to parse JSON from OpenAI nutrition response: %s",
                content,
            )
            raise NutritionEstimationFailedError(
                "Failed to parse JSON from OpenAI response"
            )

        try:
            nutrients = self._parse_nutrients(data.get("nutrients", {}))
        except Exception:
            logger.exception(
                "Failed to map nutrients from OpenAI nutrition response: %s",
                data,
            )
            raise NutritionEstimationFailedError(
                "Failed to map nutrients from OpenAI response"
            )

        return nutrients

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    def _build_user_prompt(
        self,
        user_id: UserId,
        date: DateType,
        entries: Sequence[FoodEntry],
    ) -> str:
        """
        FoodEntry 群を LLM に渡すためのテキストにまとめる。
        """

        lines: list[str] = []
        lines.append(f"User ID: {user_id.value}")
        lines.append(f"Date: {date.isoformat()}")
        lines.append("")
        lines.append("This is ONE meal (one eating occasion).")
        lines.append(
            "Each item has: name, amount, unit, servings, and optional note."
        )
        lines.append("")

        lines.append("Meal entries:")
        for idx, e in enumerate(entries, start=1):
            amount_str = (
                f"{e.amount_value} {e.amount_unit}"
                if e.amount_unit
                else f"{e.amount_value}"
            )
            serving_str = (
                f"{e.serving_count} servings"
                if e.serving_count is not None
                else "servings unknown"
            )
            note_str = f"note: {e.note}" if e.note else "note: (none)"
            lines.append(
                f"{idx}. name: {e.name}, amount: {amount_str}, "
                f"{serving_str}, {note_str}"
            )

        lines.append("")
        lines.append(
            "Estimate the nutrient intake for THIS MEAL ONLY, not the whole day."
        )

        return "\n".join(lines)

    def _parse_nutrients(
        self,
        raw_nutrients: dict[str, Any],
    ) -> list[MealNutrientIntake]:
        """
        LLM から返ってきた JSON の "nutrients" 部分を MealNutrientIntake のリストに変換する。

        - 必須 10 栄養素が揃っているか
        - 余計なキーが混ざっていないか
        - unit が期待通りか
        を検証する。
        """
        if not isinstance(raw_nutrients, dict):
            raise ValueError("nutrients must be an object")

        keys = set(raw_nutrients.keys())
        expected_keys = {code.value for code in EXPECTED_CODES}

        missing = expected_keys - keys
        extra = keys - expected_keys

        if missing:
            raise ValueError(
                f"Missing nutrients in response: {sorted(missing)}"
            )
        if extra:
            # ここでは余計なキーもエラーとして扱う（挙動を厳しめにしておく）
            raise ValueError(
                f"Unexpected nutrients in response: {sorted(extra)}"
            )

        results: list[MealNutrientIntake] = []

        for code in EXPECTED_CODES:
            key = code.value
            entry = raw_nutrients[key]

            try:
                amount_val = float(entry["amount"])
                unit = str(entry["unit"])
            except (KeyError, TypeError, ValueError) as e:
                raise ValueError(
                    f"Invalid nutrient entry for code={key}: {entry}"
                ) from e

            expected_unit = EXPECTED_UNITS[code]
            if unit != expected_unit:
                raise ValueError(
                    f"Invalid unit for {key}: expected {expected_unit}, got {unit}"
                )

            results.append(
                MealNutrientIntake(
                    code=code,
                    amount=NutrientAmount(value=amount_val, unit=unit),
                    source=NutrientSource("llm"),
                )
            )

        return results
