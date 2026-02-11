import { clientApiFetch } from '@/shared/api/client';
import {
  CreateCheckoutSessionRequest,
  CreateCheckoutSessionResponse,
  CreateCheckoutSessionResponseSchema,
  GetBillingPortalUrlResponse,
  GetBillingPortalUrlResponseSchema,
  CurrentPlanInfo,
  CurrentPlanInfoSchema,
} from '../contract/billingContract';

// ========================================
// Checkout Session 作成
// ========================================

export async function createCheckoutSession(
  request: CreateCheckoutSessionRequest = {}
): Promise<CreateCheckoutSessionResponse> {
  const response = await clientApiFetch<CreateCheckoutSessionResponse>(
    '/billing/checkout-session',
    {
      method: 'POST',
      body: request,
      headers: request.idempotency_key
        ? { 'Idempotency-Key': request.idempotency_key }
        : undefined,
    }
  );

  return CreateCheckoutSessionResponseSchema.parse(response);
}

// ========================================
// Billing Portal URL 取得
// ========================================

export async function getBillingPortalUrl(): Promise<GetBillingPortalUrlResponse> {
  const response = await clientApiFetch<GetBillingPortalUrlResponse>(
    '/billing/portal-url',
    {
      method: 'GET',
    }
  );

  return GetBillingPortalUrlResponseSchema.parse(response);
}

// ========================================
// 現在のプラン情報取得
// ========================================

export async function getCurrentPlanInfo(): Promise<CurrentPlanInfo> {
  const response = await clientApiFetch<CurrentPlanInfo>(
    '/billing/current-plan',
    {
      method: 'GET',
    }
  );

  return CurrentPlanInfoSchema.parse(response);
}

// ========================================
// ヘルパー関数
// ========================================

/**
 * Stripe Checkout画面へリダイレクトする
 */
export async function redirectToCheckout(idempotencyKey?: string): Promise<void> {
  try {
    const { checkout_url } = await createCheckoutSession({
      idempotency_key: idempotencyKey,
    });

    // 外部リダイレクト
    window.location.href = checkout_url;
  } catch (error) {
    console.error('Checkout redirect failed:', error);
    throw error;
  }
}

/**
 * Billing Portal画面へリダイレクトする
 */
export async function redirectToBillingPortal(): Promise<void> {
  try {
    const { portal_url } = await getBillingPortalUrl();

    // 外部リダイレクト
    window.location.href = portal_url;
  } catch (error) {
    console.error('Billing portal redirect failed:', error);
    throw error;
  }
}

/**
 * プラン状況を判定するヘルパー
 */
export function isPremiumPlan(planInfo: CurrentPlanInfo): boolean {
  return planInfo.user_plan === 'paid' || planInfo.is_trial_active;
}

export function isFreePlan(planInfo: CurrentPlanInfo): boolean {
  return planInfo.user_plan === 'free' && !planInfo.is_trial_active;
}

export function getDisplayPlanName(planInfo: CurrentPlanInfo): string {
  if (planInfo.is_trial_active) {
    return 'トライアル';
  }

  switch (planInfo.user_plan) {
    case 'paid':
      return 'プレミアム';
    case 'trial':
      return 'トライアル';
    case 'free':
    default:
      return 'フリー';
  }
}