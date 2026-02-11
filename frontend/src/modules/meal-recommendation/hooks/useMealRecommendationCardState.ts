/**
 * useMealRecommendationCardState - Layer 4: Feature Logic
 *
 * 食事提案カードの状態計算を管理
 */

import { calculateCardState } from '../lib/mealRecommendationHelpers';
import type { MealRecommendationCardState, MealRecommendation } from '../contract/mealRecommendationContract';

// =============================================================================
// Types
// =============================================================================

export interface UseMealRecommendationCardStateOptions {
  recommendation: MealRecommendation | null;
  isLoading: boolean;
  isGenerating: boolean;
  error: Error | null | undefined;
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useMealRecommendationCardState(
  options: UseMealRecommendationCardStateOptions
): MealRecommendationCardState {
  const { recommendation, isLoading, isGenerating, error } = options;

  return calculateCardState(isLoading, isGenerating, error, recommendation);
}
