from __future__ import annotations

from dataclasses import dataclass

from app.application.billing.ports.billing_repository_port import BillingRepositoryPort
from app.application.billing.ports.stripe_client_port import StripeClientPort
from app.application.billing.ports.uow_port import BillingUnitOfWorkPort
from app.domain.auth.value_objects import UserId
from app.domain.billing.errors import BillingAccountNotFoundError


@dataclass(slots=True)
class GetBillingPortalUrlInput:
    user_id: UserId
    return_url: str


@dataclass(slots=True)
class GetBillingPortalUrlOutput:
    portal_url: str


class GetBillingPortalUrlUseCase:
    """
    Stripe Billing Portal の URL を取得する UseCase。
    """

    def __init__(
        self,
        billing_uow: BillingUnitOfWorkPort,
        stripe_client: StripeClientPort,
    ) -> None:
        self._billing_uow = billing_uow
        self._stripe = stripe_client

    def execute(self, input: GetBillingPortalUrlInput) -> GetBillingPortalUrlOutput:
        user_id = input.user_id

        with self._billing_uow as buow:
            billing_repo: BillingRepositoryPort = buow.billing_repo
            account = billing_repo.get_by_user_id(user_id)

            if account is None or account.stripe_customer_id is None:
                raise BillingAccountNotFoundError(
                    f"BillingAccount or stripe_customer_id not found for user_id={user_id.value}"
                )

            portal_url = self._stripe.create_billing_portal_session(
                customer_id=account.stripe_customer_id,
                return_url=input.return_url,
            )

        return GetBillingPortalUrlOutput(portal_url=portal_url)
