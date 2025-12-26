from __future__ import annotations

from dataclasses import dataclass

from app.application.billing.ports.billing_repository_port import BillingRepositoryPort
from app.application.billing.ports.stripe_client_port import StripeClientPort
from app.application.billing.ports.uow_port import BillingUnitOfWorkPort
from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.application.auth.ports.uow_port import AuthUnitOfWorkPort
from app.application.auth.ports.clock_port import ClockPort
from app.domain.auth.value_objects import UserId
from app.domain.billing.entities import BillingAccount


@dataclass(slots=True)
class CreateCheckoutSessionInput:
    user_id: UserId
    success_url: str
    cancel_url: str
    customer_key: str
    session_key: str


@dataclass(slots=True)
class CreateCheckoutSessionOutput:
    checkout_url: str


class CreateCheckoutSessionUseCase:
    """
    Stripe Checkout セッションを作成し、URL を返す UseCase。

    - BillingAccount がなければ作成する。
    - stripe_customer_id がなければ Customer を作成する。
    """

    def __init__(
        self,
        billing_uow: BillingUnitOfWorkPort,
        auth_uow: AuthUnitOfWorkPort,
        stripe_client: StripeClientPort,
        clock: ClockPort,
        price_id: str,
    ) -> None:
        self._billing_uow = billing_uow
        self._auth_uow = auth_uow
        self._stripe = stripe_client
        self._clock = clock
        self._price_id = price_id

    def execute(self, input: CreateCheckoutSessionInput) -> CreateCheckoutSessionOutput:
        user_id = input.user_id

        # ユーザー情報（メールアドレス）取得
        with self._auth_uow as auow:
            user_repo: UserRepositoryPort = auow.user_repo
            user = user_repo.get_by_id(user_id)
            if user is None:
                # UserNotFoundError などを投げる前提
                from app.domain.auth.errors import UserNotFoundError

                raise UserNotFoundError(f"User not found: {user_id.value}")
            email = user.email.value

        # BillingAccount の取得 / 新規作成
        with self._billing_uow as buow:
            billing_repo: BillingRepositoryPort = buow.billing_repo

            billing_account = billing_repo.get_by_user_id(user_id)
            now = self._clock.now()

            if billing_account is None:
                # 現在の plan は user.plan をそのまま入れておく
                from app.domain.auth.value_objects import UserPlan

                billing_account = BillingAccount.create_new(
                    user_id=user_id,
                    now=now,
                    plan=user.plan if user.plan else UserPlan.FREE,
                )

            # Stripe Customer がなければ作成
            if billing_account.stripe_customer_id is None:
                customer_id = self._stripe.create_customer(
                    email=email, user_id=user_id.value, idempotency_key=input.customer_key)
                billing_account.stripe_customer_id = customer_id
                billing_account.updated_at = now
            else:
                customer_id = billing_account.stripe_customer_id

            # Checkout セッション作成
            checkout_url = self._stripe.create_checkout_session(
                customer_id=customer_id,
                price_id=self._price_id,
                success_url=input.success_url,
                cancel_url=input.cancel_url,
                user_id=user_id.value,
                idempotency_key=input.session_key,
            )

            billing_repo.save(billing_account)
            # commit は __exit__ に任せる

        return CreateCheckoutSessionOutput(checkout_url=checkout_url)
