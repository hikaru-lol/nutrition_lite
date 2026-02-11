from __future__ import annotations

import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class GenerateMealRecommendationRequest(BaseModel):
    """
    食事提案生成のリクエスト。
    """
    date: Optional[str] = Field(
        default=None,
        description="提案対象日 (YYYY-MM-DD)。省略時は今日",
        examples=["2026-02-03"]
    )


class RecommendedMealResponse(BaseModel):
    """推奨される具体的な献立"""
    title: str = Field(description="献立名", examples=["高タンパク朝食セット"])
    description: str = Field(description="献立の詳細説明", examples=["卵とアボカドでタンパク質と良質な脂質を摂取"])
    ingredients: List[str] = Field(description="主要な食材・料理名", examples=[["卵2個", "アボカド1/2個", "全粒粉パン1枚"]])
    nutrition_focus: str = Field(description="栄養的なメリット", examples=["タンパク質20g、食物繊維5g"])


class MealRecommendationResponse(BaseModel):
    """
    食事提案のレスポンス。
    """
    id: str = Field(description="提案ID", examples=["123e4567-e89b-12d3-a456-426614174000"])
    user_id: str = Field(description="ユーザーID")
    generated_for_date: datetime.date = Field(description="提案対象日", examples=["2026-02-03"])
    body: str = Field(description="メイン提案文", examples=["今日は野菜を多めに摂取することをお勧めします..."])
    tips: List[str] = Field(description="実行可能なアクション", examples=[["ブロッコリーを1食分追加", "塩分を控えめに"]])
    recommended_meals: List[RecommendedMealResponse] = Field(description="おすすめ献立3品")
    created_at: datetime.datetime = Field(description="作成日時")


class GenerateMealRecommendationResponse(BaseModel):
    """
    食事提案生成レスポンス。
    """
    recommendation: MealRecommendationResponse


class GetMealRecommendationResponse(BaseModel):
    """
    食事提案取得レスポンス。
    """
    recommendation: MealRecommendationResponse


class ListMealRecommendationsResponse(BaseModel):
    """
    食事提案一覧レスポンス。
    """
    recommendations: List[MealRecommendationResponse]