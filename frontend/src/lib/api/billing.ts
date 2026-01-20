// frontend/lib/api/billing.ts
import { apiGet, apiPost } from './client';

export type CheckoutSessionResponse = {
  checkout_url: string;
};

export type BillingPortalResponse = {
  portal_url: string;
};

export async function createCheckoutSession(): Promise<string> {
  // success_url / cancel_url をサーバー側で決める実装なら body は不要
  const res = await apiPost<CheckoutSessionResponse>(
    '/billing/checkout-session'
  );
  return res.checkout_url;
}

export async function fetchBillingPortalUrl(): Promise<string> {
  const res = await apiGet<BillingPortalResponse>('/billing/portal-url');
  return res.portal_url;
}
