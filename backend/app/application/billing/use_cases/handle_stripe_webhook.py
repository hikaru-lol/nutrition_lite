from __future__ import annotations

from dataclasses import dataclass

from app.application.billing.ports.billing_repository_port import BillingRepositoryPort
from app.application.billing.ports.stripe_client_port import StripeClientPort
from app.application.billing.ports.uow_port import BillingUnitOfWorkPort
from app.application.auth.ports.uow_port import AuthUnitOfWorkPort
from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.application.auth.ports.clock_port import ClockPort
from app.domain.auth.value_objects import UserId, UserPlan
from app.domain.billing.entities import BillingSubscriptionStatus
from app.domain.billing.entities import BillingAccount
from app.domain.billing.errors import BillingAccountNotFoundError, BillingInconsistentStateError


@dataclass(slots=True)
class HandleStripeWebhookInput:
    payload: bytes
    signature_header: str


class HandleStripeWebhookUseCase:
    """
    Stripe Webhook イベントを処理して BillingAccount / User.plan を更新する UseCase。
    """

    def __init__(
        self,
        billing_uow: BillingUnitOfWorkPort,
        auth_uow: AuthUnitOfWorkPort,
        stripe_client: StripeClientPort,
        clock: ClockPort,
    ) -> None:
        self._billing_uow = billing_uow
        self._auth_uow = auth_uow
        self._stripe = stripe_client
        self._clock = clock

    def execute(self, input: HandleStripeWebhookInput) -> None:
        event = self._stripe.construct_event(
            payload=input.payload,
            sig_header=input.signature_header,
        )

        event_type = event["type"]
        data = event["data"]["object"]

        # 1. checkout.session.completed: サブスク開始のトリガー
        if event_type == "checkout.session.completed":
            self._handle_checkout_session_completed(data)
        # 2. customer.subscription.updated / deleted: サブスク状態更新
        elif event_type in ("customer.subscription.updated", "customer.subscription.deleted"):
            self._handle_subscription_updated(data)
        else:
            # 他のイベントは今は無視（ログだけ吐いてもよい）
            return

    # ------------------------------------------------------------------

    def _handle_checkout_session_completed(self, session_obj: dict) -> None:
        """
        checkout.session.completed 用の処理。

        - session.metadata.user_id または customer の metadata から user_id を特定。
        - subscription_id を取得して BillingAccount / User.plan を更新。
        """
        # user_id の取り出しロジックは実際の Checkout 作成時の metadata に合わせて調整
        user_id_raw = (
            session_obj.get("metadata", {}) or {}
        ).get("user_id")

        if not user_id_raw:
            raise BillingInconsistentStateError(
                "checkout.session has no user_id metadata")

        user_id = UserId(user_id_raw)
        subscription_id = session_obj.get("subscription")  # "sub_xxx"
        customer_id = session_obj.get("customer")          # "cus_xxx"

        if not subscription_id or not customer_id:
            raise BillingInconsistentStateError(
                "checkout.session is missing subscription or customer id"
            )

        # Subscription 情報を取得
        sub_info = self._stripe.retrieve_subscription(subscription_id)
        now = self._clock.now()

        # BillingAccount / User.plan 更新
        with self._billing_uow as buow, self._auth_uow as auow:
            billing_repo: BillingRepositoryPort = buow.billing_repo
            user_repo: UserRepositoryPort = auow.user_repo

            account = billing_repo.get_by_user_id(user_id)
            if account is None:
                # 無ければ新規（FREE ベース）から作成
                account = BillingAccount.create_new(
                    user_id=user_id,
                    now=now,
                    plan=UserPlan.FREE,
                )

            status = self._map_subscription_status(sub_info.status)
            # trial 中かどうかは user から判定
            user = user_repo.get_by_id(user_id)
            if user is None:
                raise BillingAccountNotFoundError(
                    f"User not found: {user_id.value}")

            # UserPlan を決定
            if user.trial_info.is_trial_active(now):
                new_plan = UserPlan.TRIAL
            elif status == BillingSubscriptionStatus.ACTIVE:
                new_plan = UserPlan.PAID
            else:
                new_plan = UserPlan.FREE

            # BillingAccount 更新
            account.update_subscription(
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription_id,
                status=status,
                plan=new_plan,
                now=now,
            )
            billing_repo.save(account)

            # User.plan 更新
            user.plan = new_plan
            user_repo.save(user)  # save がある前提

    def _handle_subscription_updated(self, sub_obj: dict) -> None:
        """
        customer.subscription.updated / deleted 用の処理。

        - subscription id / customer id から user_id を特定する方法はプロジェクト次第。
        - ここでは BillingAccount の stripe_subscription_id 経由で user を逆引きする想定もあり得る。
        """
        subscription_id = sub_obj.get("id")
        status_raw = sub_obj.get("status")

        if not subscription_id or not status_raw:
            raise BillingInconsistentStateError(
                "subscription event missing id or status"
            )

        status = self._map_subscription_status(status_raw)
        now = self._clock.now()

        # Subscription ID から BillingAccount を引き、その user の plan を調整
        with self._billing_uow as buow, self._auth_uow as auow:
            billing_repo: BillingRepositoryPort = buow.billing_repo
            user_repo: UserRepositoryPort = auow.user_repo

            # Subscription ID からアカウントを逆引きする API が必要になるが、
            # まずは subscription_id でフィルタする get_by_subscription_id を BillingRepo に足してもよい。
            # ここでは TODO としておく。
            # account = billing_repo.get_by_subscription_id(subscription_id)
            # if account is None: ... というイメージ。

            # TODO: 実装時に BillingRepositoryPort に
            # get_by_subscription_id(...) を追加して対応する。

            # このフェーズではスケルトンのみ提示。
            pass

    def _map_subscription_status(self, stripe_status: str) -> BillingSubscriptionStatus:
        """
        stripe.Subscription.status を BillingSubscriptionStatus にマッピングする。
        """
        stripe_status = stripe_status.lower()
        if stripe_status == "active":
            return BillingSubscriptionStatus.ACTIVE
        if stripe_status in ("past_due", "unpaid"):
            return BillingSubscriptionStatus.PAST_DUE
        if stripe_status in ("canceled", "incomplete_expired"):
            return BillingSubscriptionStatus.CANCELED
        if stripe_status in ("incomplete",):
            return BillingSubscriptionStatus.INCOMPLETE
        return BillingSubscriptionStatus.NONE
