from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


# =====================================================================
# 共通 DTO（エンドポイントのレスポンスにも使う形）
# =====================================================================


@dataclass(slots=True)
class TargetNutrientDTO:
    """
    1つの栄養素に対するターゲット値（DTO）。

    - code   : NutrientCode.value （例: "protein"）
    - amount : NutrientAmount.value
    - unit   : NutrientAmount.unit （例: "g", "mg", "kcal"）
    - source : NutrientSource.value （"llm" / "manual" / "user_input"）
    """

    code: str
    amount: float
    unit: str
    source: str


@dataclass(slots=True)
class TargetDTO:
    """
    1つのターゲット定義の DTO。

    Domain: TargetDefinition を API / UseCase 用にフラットにしたもの。
    """

    id: str
    user_id: str

    title: str
    goal_type: str                 # GoalType.value
    goal_description: Optional[str]
    activity_level: str            # ActivityLevel.value

    is_active: bool

    nutrients: List[TargetNutrientDTO]

    llm_rationale: Optional[str]
    disclaimer: Optional[str]

    created_at: datetime
    updated_at: datetime


# =====================================================================
# UseCase 入力 DTO
# =====================================================================

# --- CreateTarget -----------------------------------------------------


@dataclass(slots=True)
class CreateTargetInputDTO:
    """
    新しい TargetDefinition を作成するための入力 DTO。

    - user_id は認証済みユーザー
    - 栄養素の中身は TargetGeneratorPort に任せる前提で、
      ここでは「目標情報（タイトル / 目的 / 活動レベル）」のみを受け取る。
    """

    user_id: str

    title: str
    goal_type: str                 # GoalType.value ("weight_loss" など)
    goal_description: Optional[str]
    # ActivityLevel.value ("low" / "normal" / "high")
    activity_level: str


# --- GetTarget / GetActive / List ------------------------------------


@dataclass(slots=True)
class GetTargetInputDTO:
    """
    特定の TargetDefinition を1件取得するための入力 DTO。
    """

    user_id: str
    target_id: str


@dataclass(slots=True)
class GetActiveTargetInputDTO:
    """
    現在 Active な TargetDefinition を取得するための入力 DTO。
    """

    user_id: str


@dataclass(slots=True)
class ListTargetsInputDTO:
    """
    ユーザーに紐づく TargetDefinition 一覧を取得するための入力 DTO。

    - limit / offset はページング用（省略時は実装側のデフォルトに任せる）
    """

    user_id: str
    limit: Optional[int] = None
    offset: int = 0


# --- UpdateTarget -----------------------------------------------------


@dataclass(slots=True)
class UpdateTargetNutrientDTO:
    """
    TargetDefinition の nutrients を部分更新するためのパッチ DTO。

    - code   : 更新対象の NutrientCode.value
    - amount : None の場合は量を変更しない
    - unit   : None の場合は単位を変更しない
    """

    code: str
    amount: Optional[float] = None
    unit: Optional[str] = None


@dataclass(slots=True)
class UpdateTargetInputDTO:
    """
    TargetDefinition の「部分更新（PATCH 的）」の入力 DTO。

    - None のフィールドは「更新しない」
    - 値が入っているフィールドだけを更新する
    - nutrients は、指定した code に対して amount/unit を上書きするためのパッチ。
    """

    user_id: str
    target_id: str

    title: Optional[str] = None
    goal_type: Optional[str] = None           # GoalType.value
    goal_description: Optional[str] = None
    activity_level: Optional[str] = None      # ActivityLevel.value

    llm_rationale: Optional[str] = None
    disclaimer: Optional[str] = None

    nutrients: Optional[List[UpdateTargetNutrientDTO]] = None


# --- ActivateTarget ---------------------------------------------------


@dataclass(slots=True)
class ActivateTargetInputDTO:
    """
    指定した TargetDefinition を Active にするための入力 DTO。

    - ユースケース内で、同一ユーザーの既存ターゲットをすべて inactive にしてから
      この target_id を active にする。
    """

    user_id: str
    target_id: str
