from __future__ import annotations
from app.domain.billing.errors import BillingAccountNotFoundError
from stripe import error as stripe_error
from app.settings import settings
from app.domain.auth.value_objects import UserId
from app.di.container import (
    get_create_checkout_session_use_case,
    get_billing_portal_url_use_case,
    get_handle_stripe_webhook_use_case,
)
from app.application.billing.use_cases.handle_stripe_webhook import (
    HandleStripeWebhookInput,
    HandleStripeWebhookUseCase,
)
from app.application.billing.use_cases.get_billing_portal_url import (
    GetBillingPortalUrlInput,
    GetBillingPortalUrlUseCase,
)
from app.application.billing.use_cases.create_checkout_session import (
    CreateCheckoutSessionInput,
    CreateCheckoutSessionUseCase,
)
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.api.http.schemas.billing import (
    CheckoutSessionResponse,
    BillingPortalUrlResponse,
)
from app.api.http.dependencies.auth import get_current_user_dto

from fastapi import APIRouter, Depends, HTTPException, Request, status, Header
from uuid import uuid4
from logging import getLogger

logger = getLogger(__name__)


router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post(
    "/checkout-session",
    response_model=CheckoutSessionResponse,
    responses={
        400: {"description": "Billing inconsistent state"},
        401: {"description": "Unauthorized"},
        404: {"description": "Billing account not found"},
        500: {"description": "Failed to create checkout session"},
    },
)
def create_checkout_session(
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: CreateCheckoutSessionUseCase = Depends(
        get_create_checkout_session_use_case),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
) -> CheckoutSessionResponse:
    """
    Stripe Checkout セッションを作成し、その URL を返す。

    - フロントからはこの URL にリダイレクトすればサブスク購入画面に飛ぶ。
    """
    if not idempotency_key:
        idempotency_key = str(uuid4())

    customer_key = f"cus:{idempotency_key}"[:255]
    session_key = f"cs:{idempotency_key}"[:255]

    user_id = UserId(current_user.id)

    # 成功時の戻り URL / キャンセル URL は settings から組み立てる前提
    success_url = settings.STRIPE_CHECKOUT_SUCCESS_URL
    cancel_url = settings.STRIPE_CHECKOUT_CANCEL_URL

    input_dto = CreateCheckoutSessionInput(
        user_id=user_id,
        success_url=success_url,
        cancel_url=cancel_url,
        customer_key=customer_key,
        session_key=session_key,
    )

    try:
        output = use_case.execute(input_dto)
    except Exception as e:
        logger.exception("Failed to create checkout session")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session.",
        ) from e

    return CheckoutSessionResponse(checkout_url=output.checkout_url)


@router.get(
    "/portal-url",
    response_model=BillingPortalUrlResponse,
    responses={
        400: {"description": "Billing account not found"},
        401: {"description": "Unauthorized"},
    },
)
def get_billing_portal_url(
    current_user: AuthUserDTO = Depends(get_current_user_dto),
    use_case: GetBillingPortalUrlUseCase = Depends(
        get_billing_portal_url_use_case),
) -> BillingPortalUrlResponse:
    """
    Stripe Billing Portal の URL を取得する。

    - ここからユーザーはサブスクのキャンセルや支払い方法変更などを行う。
    """
    user_id = UserId(current_user.id)
    return_url = settings.STRIPE_PORTAL_RETURN_URL

    input_dto = GetBillingPortalUrlInput(
        user_id=user_id,
        return_url=return_url,
    )

    try:
        output = use_case.execute(input_dto)
    except BillingAccountNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Billing account or Stripe customer is not configured.",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create billing portal session.",
        ) from e

    return BillingPortalUrlResponse(portal_url=output.portal_url)


@router.post(
    "/stripe/webhook",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid Stripe webhook payload or signature"},
        500: {"description": "Failed to handle Stripe webhook"},
    },
)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="Stripe-Signature"),
    use_case: HandleStripeWebhookUseCase = Depends(
        get_handle_stripe_webhook_use_case
    ),
) -> dict:
    """
    Stripe からの Webhook イベントを受け取り、BillingAccount / User.plan を更新する。

    - Stripe-Signature ヘッダを使用して署名検証を行う。
    """
    payload = await request.body()
    input_dto = HandleStripeWebhookInput(
        payload=payload,
        signature_header=stripe_signature,
    )

    try:
        use_case.execute(input_dto)
    except stripe_error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe webhook payload or signature.",
        )
    except Exception:
        logger.exception("stripe_webhook failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to handle Stripe webhook.",
        )

    # Stripe は 2xx を返せば OK（ボディは空 or {} でよい）
    return {}
