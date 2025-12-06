from __future__ import annotations

from pydantic import BaseModel, HttpUrl


class CheckoutSessionResponse(BaseModel):
    checkout_url: HttpUrl | str


class BillingPortalUrlResponse(BaseModel):
    portal_url: HttpUrl | str
