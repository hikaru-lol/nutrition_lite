from __future__ import annotations

import os
from typing import Any

import stripe

from app.application.billing.ports.stripe_client_port import (
    StripeClientPort,
    StripeSubscriptionInfo,
)


class StripeClient(StripeClientPort):
    """
    StripeClientPort の stripe-python 実装。

    - STRIPE_API_KEY / STRIPE_WEBHOOK_SECRET は環境変数から読む想定。
    """

    def __init__(self, api_key: str | None = None, webhook_secret: str | None = None) -> None:
        self._api_key = api_key or os.getenv("STRIPE_API_KEY", "")
        self._webhook_secret = webhook_secret or os.getenv(
            "STRIPE_WEBHOOK_SECRET", "")
        stripe.api_key = self._api_key

    # --- Checkout / Portal -------------------------------------------

    def create_customer(self, email: str, user_id: str, idempotency_key: str) -> str:
        """
        メールアドレスと user_id を metadata に入れて Customer を作る。
        すでに同じメールの Customer がいるかどうかを探すロジックは
        必要に応じて追加してもよい。
        """
        customer = stripe.Customer.create(
            email=email,
            metadata={"user_id": user_id},
            idempotency_key=idempotency_key,
        )
        return customer.id

    def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        user_id: str,
        idempotency_key: str,
    ) -> str:
        """
        サブスク用の Checkout セッションを作成し、その URL を返す。
        """
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=customer_id,
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": user_id,
            },
            client_reference_id=user_id,
            idempotency_key=idempotency_key,
        )
        return session.url

    def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str,
    ) -> str:
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return portal_session.url

    # --- Webhook / Subscription --------------------------------------

    def construct_event(self, payload: bytes, sig_header: str) -> Any:
        """
        Stripe.Webhook.construct_event をラップし、署名検証も行う。
        """
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=self._webhook_secret,
        )
        return event

    def retrieve_subscription(self, subscription_id: str) -> StripeSubscriptionInfo:
        sub = stripe.Subscription.retrieve(subscription_id)
        return StripeSubscriptionInfo(id=sub.id, status=sub.status)
