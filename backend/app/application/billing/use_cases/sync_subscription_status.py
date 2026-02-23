from __future__ import annotations

from app.application.billing.ports.billing_repository_port import BillingRepositoryPort
from app.application.billing.ports.stripe_client_port import StripeClientPort
from app.domain.billing.entities import UserId


class SyncSubscriptionStatusUseCase:
    """
    StripeからサブスクリプションステータスをDBに同期するユースケース
    """

    def __init__(
        self,
        billing_repo: BillingRepositoryPort,
        stripe_client: StripeClientPort
    ):
        self._billing_repo = billing_repo
        self._stripe_client = stripe_client

    def execute(self, user_id: UserId) -> None:
        """Stripeからサブスクリプションステータスを同期"""
        account = self._billing_repo.get_by_user_id(user_id)
        if not account:
            raise ValueError(f"Billing account not found for user: {user_id.value}")

        if not account.stripe_subscription_id:
            raise ValueError(f"No Stripe subscription found for user: {user_id.value}")

        # Stripeから最新のサブスクリプション情報を取得
        stripe_sub = self._stripe_client.retrieve_subscription(account.stripe_subscription_id.value)

        # ステータスを更新
        account.sync_from_stripe(stripe_sub.status)

        # プランを更新
        if stripe_sub.status == "active":
            account.update_plan("paid")
        else:
            account.update_plan("free")

        self._billing_repo.save(account)