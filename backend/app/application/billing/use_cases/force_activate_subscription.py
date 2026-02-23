from __future__ import annotations

from app.application.billing.ports.billing_repository_port import BillingRepositoryPort
from app.domain.billing.entities import UserId


class ForceActivateSubscriptionUseCase:
    """
    開発環境専用: サブスクリプションを強制的にactiveにするユースケース
    """

    def __init__(self, billing_repo: BillingRepositoryPort):
        self._billing_repo = billing_repo

    def execute(self, user_id: UserId) -> None:
        """サブスクリプションを強制的にactiveにする"""
        account = self._billing_repo.get_by_user_id(user_id)
        if not account:
            raise ValueError(f"Billing account not found for user: {user_id.value}")

        account.force_activate()
        self._billing_repo.save(account)