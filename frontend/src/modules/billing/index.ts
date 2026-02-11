// ========================================
// Billing Module Exports
// ========================================

// Contract (型定義・スキーマ)
export type {
  UserPlan,
  CurrentPlanInfo,
  CreateCheckoutSessionRequest,
  CreateCheckoutSessionResponse,
  GetBillingPortalUrlResponse,
  BillingSubscriptionStatus,
  BillingError,
} from './contract/billingContract';

export {
  UserPlanSchema,
  CurrentPlanInfoSchema,
  CreateCheckoutSessionRequestSchema,
  CreateCheckoutSessionResponseSchema,
  GetBillingPortalUrlResponseSchema,
  BillingSubscriptionStatusSchema,
  BillingErrorSchema,
  PLAN_DEFINITIONS,
  BETA_NOTICE,
  FEATURE_LIMITS,
  checkFeatureLimit,
} from './contract/billingContract';

// API Client
export {
  createCheckoutSession,
  getBillingPortalUrl,
  getCurrentPlanInfo,
  redirectToCheckout,
  redirectToBillingPortal,
  isPremiumPlan,
  getDisplayPlanName,
} from './api/billingClient';

// Model (状態管理hooks)
export {
  useBillingPageModel,
  useFeatureLimitCheck,
  useCurrentPlan,
} from './model/useBillingPageModel';

// UI Components
export { BillingPlanPage } from './ui/BillingPlanPage';
export { BillingManagePage } from './ui/BillingManagePage';
export { BillingSuccessPage } from './ui/BillingSuccessPage';
export { BillingCancelPage } from './ui/BillingCancelPage';