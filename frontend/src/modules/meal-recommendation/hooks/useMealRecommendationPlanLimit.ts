/**
 * useMealRecommendationPlanLimit - Layer 4: Feature Logic
 *
 * 食事提案のプラン制限チェックを管理
 */

import { useFeatureLimitCheck } from '@/modules/billing';
import type { MealRecommendation } from '../contract/mealRecommendationContract';

// =============================================================================
// Types
// =============================================================================

export interface UseMealRecommendationPlanLimitOptions {
  recommendations: MealRecommendation[] | undefined;
}

export interface MealRecommendationPlanLimitModel {
  planLimit: {
    requiresUpgrade: boolean;
    limit: number | null;
    remaining: number | null;
  };
  currentCount: number;
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useMealRecommendationPlanLimit(
  options: UseMealRecommendationPlanLimitOptions
): MealRecommendationPlanLimitModel {
  const { recommendations } = options;
  const { checkMealRecommendationLimit } = useFeatureLimitCheck();

  // プラン制限チェック
  // Note: 今日生成された推奨の数をカウント（履歴から計算）
  // バックエンドAPIが日次カウントを返すようになれば、そちらを優先すべき
  const currentCount = recommendations?.filter(r =>
    new Date(r.created_at).toDateString() === new Date().toDateString()
  ).length || 0;

  const planLimit = checkMealRecommendationLimit(currentCount);

  return {
    planLimit,
    currentCount,
  };
}
