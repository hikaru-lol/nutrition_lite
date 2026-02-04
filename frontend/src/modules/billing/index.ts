// ========================================
// Billing Module Exports
// ========================================

// Contract (型定義・スキーマ)
export type {
  UserPlan,
  BillingPlan,
  CurrentPlanInfo,
  CreateCheckoutRequest,
  CreateCheckoutResponse,
  GetBillingPortalResponse,
} from './contract/billingContract';

export {
  UserPlanSchema,
  BillingPlanSchema,
  CurrentPlanInfoSchema,
  CreateCheckoutRequestSchema,
  CreateCheckoutResponseSchema,
  GetBillingPortalResponseSchema,
  PLAN_DEFINITIONS,
  BETA_NOTICE,
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