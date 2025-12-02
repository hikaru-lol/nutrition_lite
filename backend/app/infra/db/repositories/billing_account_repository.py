from __future__ import annotations

from typing import Optional
from uuid import UUID

from typing import cast

from sqlalchemy.orm import Session

from app.application.billing.ports.billing_repository_port import BillingRepositoryPort
from app.domain.auth.value_objects import UserId, UserPlan
from app.domain.billing.entities import (
    BillingAccount,
    BillingAccountId,
    BillingSubscriptionStatus,
)
from app.infra.db.models.billing_account import BillingAccountModel


class SqlAlchemyBillingAccountRepository(BillingRepositoryPort):
    """
    BillingRepositoryPort の SQLAlchemy 実装。
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Entity <-> Model 変換
    # ------------------------------------------------------------------

    def _to_entity(self, model: BillingAccountModel) -> BillingAccount:
        # subscription_status の文字列を Enum に戻す
        try:
            raw_status = cast(str, model.subscription_status)
            status = BillingSubscriptionStatus[raw_status.upper()]
        except KeyError:
            status = BillingSubscriptionStatus.NONE

        # current_plan の文字列を UserPlan に戻す
        plan = UserPlan(model.current_plan)

        return BillingAccount(
            id=BillingAccountId(str(model.id)),
            user_id=UserId(str(model.user_id)),
            stripe_customer_id=model.stripe_customer_id,
            stripe_subscription_id=model.stripe_subscription_id,
            subscription_status=status,
            current_plan=plan,
            updated_at=model.updated_at,
        )

    def _from_entity(self, account: BillingAccount) -> BillingAccountModel:
        return BillingAccountModel(
            id=UUID(account.id.value),
            user_id=UUID(account.user_id.value),
            stripe_customer_id=account.stripe_customer_id,
            stripe_subscription_id=account.stripe_subscription_id,
            subscription_status=account.subscription_status.name.lower(),
            current_plan=account.current_plan.value,
            updated_at=account.updated_at,
        )

    # ------------------------------------------------------------------
    # Port 実装
    # ------------------------------------------------------------------

    def get_by_user_id(self, user_id: UserId) -> Optional[BillingAccount]:
        model: BillingAccountModel | None = (
            self._session.query(BillingAccountModel)
            .filter(BillingAccountModel.user_id == UUID(user_id.value))
            .one_or_none()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def save(self, account: BillingAccount) -> None:
        """
        BillingAccount を保存する。

        - id ベースで insert / update を吸収するため merge を利用。
        - トランザクション境界（commit/rollback）は UoW 側で管理する前提。
        """
        model = self._from_entity(account)
        self._session.merge(model)
