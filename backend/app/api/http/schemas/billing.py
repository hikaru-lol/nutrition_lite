from __future__ import annotations

from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime


class CheckoutSessionResponse(BaseModel):
    checkout_url: HttpUrl | str


class BillingPortalUrlResponse(BaseModel):
    portal_url: HttpUrl | str


class CurrentPlanResponse(BaseModel):
    """
    現在のユーザープラン情報のレスポンス。

    AuthUserDTO から必要な情報のみを抽出して返す。
    フロントエンドの billing 機能で使用される。
    """
    user_plan: str = Field(
        description="ユーザーのプラン: 'trial', 'free', 'paid'",
        example="free"
    )
    is_trial_active: bool = Field(
        description="トライアルが現在有効かどうか（trial_ends_at と現在時刻を比較した結果）",
        example=False
    )
    trial_ends_at: datetime | None = Field(
        default=None,
        description="トライアル終了日時。トライアル未利用の場合は null",
        example=None
    )
