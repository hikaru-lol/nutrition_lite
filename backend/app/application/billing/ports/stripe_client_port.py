from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(slots=True)
class StripeSubscriptionInfo:
    id: str
    status: str  # "active", "canceled", "past_due", ...


class StripeClientPort(Protocol):
    """
    Stripe 連携を抽象化するポート。

    - 実装は stripe-python を内部で利用してよいが、
      UseCase からはこのインターフェース越しにしか見えないようにする。
    """

    # --- Checkout / Portal -------------------------------------------

    def create_customer(self, email: str, user_id: str) -> str:
        """
        Stripe 上に Customer を作成し、その ID を返す ("cus_xxx")。
        すでに存在する場合は既存 ID を返す実装でもよい。
        """
        ...

    def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
    ) -> str:
        """
        サブスク用の Checkout セッションを作成し、その URL を返す。
        """
        ...

    def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str,
    ) -> str:
        """
        Billing Portal セッションを作成し、その URL を返す。
        """
        ...

    # --- Webhook / Subscription --------------------------------------

    def construct_event(self, payload: bytes, sig_header: str) -> Any:
        """
        Stripe Webhook の payload と署名ヘッダから event オブジェクトを構築する。
        署名検証に失敗した場合は例外を投げる。
        """
        ...

    def retrieve_subscription(self, subscription_id: str) -> StripeSubscriptionInfo:
        """
        Subscription ID から現在の subscription 情報を取得する。
        """
        ...
