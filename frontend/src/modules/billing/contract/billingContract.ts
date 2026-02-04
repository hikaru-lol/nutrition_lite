import { z } from 'zod';

// ========================================
// ユーザープラン関連
// ========================================

export const UserPlanSchema = z.enum(['trial', 'free', 'paid']);
export type UserPlan = z.infer<typeof UserPlanSchema>;

export const BillingSubscriptionStatusSchema = z.enum([
  'none',
  'active',
  'past_due',
  'canceled',
  'incomplete'
]);
export type BillingSubscriptionStatus = z.infer<typeof BillingSubscriptionStatusSchema>;

// ========================================
// API Request/Response スキーマ
// ========================================

// Checkout Session 作成
export const CreateCheckoutSessionRequestSchema = z.object({
  idempotency_key: z.string().optional(),
});
export type CreateCheckoutSessionRequest = z.infer<typeof CreateCheckoutSessionRequestSchema>;

export const CreateCheckoutSessionResponseSchema = z.object({
  checkout_url: z.string().url(),
});
export type CreateCheckoutSessionResponse = z.infer<typeof CreateCheckoutSessionResponseSchema>;

// Billing Portal URL 取得
export const GetBillingPortalUrlResponseSchema = z.object({
  portal_url: z.string().url(),
});
export type GetBillingPortalUrlResponse = z.infer<typeof GetBillingPortalUrlResponseSchema>;

// 現在のプラン情報
export const CurrentPlanInfoSchema = z.object({
  user_plan: UserPlanSchema,
  subscription_status: BillingSubscriptionStatusSchema,
  is_trial_active: z.boolean(),
  trial_ends_at: z.string().nullable().optional(), // ISO datetime, null許可
  subscription_id: z.string().nullable().optional(), // null許可
  customer_id: z.string().nullable().optional(), // null許可
});
export type CurrentPlanInfo = z.infer<typeof CurrentPlanInfoSchema>;

// ========================================
// プラン定義
// ========================================

export interface PlanFeatures {
  name: string;
  price: string;
  description: string;
  features: string[];
  limitations?: string[];
  isPopular?: boolean;
}

export const PLAN_DEFINITIONS = {
  free: {
    name: 'フリープラン',
    price: '無料',
    description: '基本的な栄養管理機能',
    features: [
      '食事記録の登録・管理',
      '基本的な栄養データ表示',
      '月間サマリー',
    ],
    limitations: [
      '食事提案は月5回まで',
      '詳細な栄養解析なし',
      'AI栄養アドバイス限定版',
    ],
  },
  paid: {
    name: 'プレミアムプラン',
    price: '¥980/月',
    description: '全機能利用可能',
    features: [
      '食事記録の登録・管理',
      '無制限の食事提案',
      '詳細な栄養解析',
      'AI栄養アドバイス（フル機能）',
      '目標に応じたカスタム提案',
      '月間・週間詳細レポート',
      'エクスポート機能',
    ],
    isPopular: true,
  },
} as const satisfies Record<string, PlanFeatures>;

// ========================================
// エラー型
// ========================================

export const BillingErrorSchema = z.object({
  code: z.enum([
    'billing_account_not_found',
    'checkout_session_failed',
    'portal_access_denied',
    'subscription_limit_exceeded',
    'payment_required',
  ]),
  message: z.string(),
  details: z.record(z.unknown()).optional(),
});
export type BillingError = z.infer<typeof BillingErrorSchema>;

// ========================================
// 機能制限チェック用
// ========================================

export const FEATURE_LIMITS = {
  meal_recommendations_per_month: {
    free: 5,
    paid: null, // unlimited
    trial: null, // unlimited
  },
  detailed_analysis: {
    free: false,
    paid: true,
    trial: true,
  },
  export_data: {
    free: false,
    paid: true,
    trial: false,
  },
} as const;

// 機能制限チェックヘルパー
export function checkFeatureLimit(
  feature: keyof typeof FEATURE_LIMITS,
  plan: UserPlan,
  currentUsage?: number
): {
  allowed: boolean;
  limit?: number | null;
  remaining?: number;
} {
  const limits = FEATURE_LIMITS[feature];
  const limit = limits[plan];

  if (typeof limit === 'boolean') {
    return { allowed: limit, limit };
  }

  if (limit === null) {
    return { allowed: true, limit: null };
  }

  if (typeof limit === 'number' && typeof currentUsage === 'number') {
    const remaining = Math.max(0, limit - currentUsage);
    return {
      allowed: currentUsage < limit,
      limit,
      remaining,
    };
  }

  return { allowed: true, limit };
}

// ========================================
// β版表示用
// ========================================

export const BETA_NOTICE = {
  title: 'β版・テスト運用中',
  message: '現在β版として運用中のため、実際の課金処理は発生しません。テスト用のクレジットカード情報をご使用ください。',
  testCard: '4242 4242 4242 4242',
} as const;