/**
 * useMealRecommendationModel - Layer 3: Page Aggregation
 *
 * 食事提案の機能を統合（useTodayPageModelと同じパターン）
 */

import { useMealRecommendationQuery } from '../hooks/useMealRecommendationQuery';
import { useMealRecommendationGeneration } from '../hooks/useMealRecommendationGeneration';
import { useMealRecommendationCardState } from '../hooks/useMealRecommendationCardState';
import { useMealRecommendationPlanLimit } from '../hooks/useMealRecommendationPlanLimit';

// =============================================================================
// Types
// =============================================================================

export interface UseMealRecommendationModelOptions {
  date?: string;  // YYYY-MM-DD
  enabled?: boolean;
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useMealRecommendationModel(options: UseMealRecommendationModelOptions = {}) {
  const { date, enabled = true } = options;

  // Layer 4: Feature Hooks
  const query = useMealRecommendationQuery({ date, enabled });
  const generation = useMealRecommendationGeneration({ date });
  const cardState = useMealRecommendationCardState({
    recommendation: query.recommendation,
    isLoading: query.isLoading,
    isGenerating: generation.isGenerating,
    error: query.error || generation.generateError,
  });
  const limits = useMealRecommendationPlanLimit({
    recommendations: query.recommendations,
  });

  // 統合して返す
  return {
    // 状態情報
    state: {
      cardState,
      isLoading: query.isLoading,
      isGenerating: generation.isGenerating,
      isLoadingHistory: query.isLoadingHistory,
      error: query.error || generation.generateError,
    },

    // データ
    data: {
      recommendation: query.recommendation,
      recommendations: query.recommendations,
    },

    // プラン制限情報
    limits: {
      planLimit: limits.planLimit,
      currentCount: limits.currentCount,
    },

    // アクション
    actions: {
      generate: generation.generate,
      refresh: query.refetch,
      loadHistory: query.loadHistory,
    },
  };
}
