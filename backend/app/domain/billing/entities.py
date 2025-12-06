from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto

from app.domain.auth.value_objects import UserId
from app.domain.auth.value_objects import UserPlan  # "trial" / "free" / "paid"


class BillingSubscriptionStatus(Enum):
    """
    Stripe サブスクリプションの内部表現。

    - Stripe の status を簡略化したもの。
    """

    NONE = auto()       # サブスクなし
    ACTIVE = auto()     # 有効
    PAST_DUE = auto()   # 支払い遅延など
    CANCELED = auto()   # キャンセル済み
    INCOMPLETE = auto()  # 初回請求未完了など


@dataclass(slots=True)
class BillingAccountId:
    value: str

    @classmethod
    def new(cls) -> BillingAccountId:
        from uuid import uuid4
        return cls(value=str(uuid4()))


@dataclass(slots=True)
class BillingAccount:
    """
    1ユーザーに対応する課金アカウント情報。

    - stripe_customer_id: Stripe 上の Customer ID ("cus_xxx")
    - stripe_subscription_id: Stripe 上の Subscription ID ("sub_xxx") / None
    - subscription_status: 内部的なサブスク状態
    - current_plan: アプリケーション側で見ている論理プラン（User.plan と同期させる）
    """

    id: BillingAccountId
    user_id: UserId

    stripe_customer_id: str | None
    stripe_subscription_id: str | None
    subscription_status: BillingSubscriptionStatus

    current_plan: UserPlan
    updated_at: datetime

    @classmethod
    def create_new(
        cls,
        user_id: UserId,
        now: datetime,
        plan: UserPlan,
    ) -> BillingAccount:
        """
        初回 BillingAccount 作成用のファクトリ。
        サブスクなし (NONE) からスタートする。
        """
        return cls(
            id=BillingAccountId.new(),
            user_id=user_id,
            stripe_customer_id=None,
            stripe_subscription_id=None,
            subscription_status=BillingSubscriptionStatus.NONE,
            current_plan=plan,
            updated_at=now,
        )

    def update_subscription(
        self,
        stripe_customer_id: str | None,
        stripe_subscription_id: str | None,
        status: BillingSubscriptionStatus,
        plan: UserPlan,
        now: datetime,
    ) -> None:
        """
        Stripe サブスク状態の更新時に呼び出すメソッド。

        - Webhook や Checkout 完了後に利用する想定。
        """
        self.stripe_customer_id = stripe_customer_id
        self.stripe_subscription_id = stripe_subscription_id
        self.subscription_status = status
        self.current_plan = plan
        self.updated_at = now
