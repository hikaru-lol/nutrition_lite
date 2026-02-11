/**
 * useMealRecommendationGeneration - Layer 4: Feature Logic
 *
 * 食事提案の生成処理を管理
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { qk } from '@/shared/lib/query/keys';
import { mealRecommendationApi } from '../api/mealRecommendationClient';
import type { GenerateMealRecommendationRequest } from '../contract/mealRecommendationContract';

// =============================================================================
// Types
// =============================================================================

export interface UseMealRecommendationGenerationOptions {
  date?: string;  // YYYY-MM-DD
}

export interface MealRecommendationGenerationModel {
  // アクション
  generate: (data?: GenerateMealRecommendationRequest) => void;

  // 状態
  isGenerating: boolean;
  generateError: Error | null;
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useMealRecommendationGeneration(
  options: UseMealRecommendationGenerationOptions = {}
): MealRecommendationGenerationModel {
  const { date } = options;
  const queryClient = useQueryClient();

  // ミューテーション：食事提案生成
  const generateMutation = useMutation({
    mutationFn: (data: GenerateMealRecommendationRequest) =>
      mealRecommendationApi.generate(data),
    onSuccess: () => {
      // 生成成功時にクエリを無効化して最新データを取得
      queryClient.invalidateQueries({
        queryKey: qk.mealRecommendation.byDate(date || 'today')
      });
      queryClient.invalidateQueries({
        queryKey: qk.mealRecommendation.list()
      });
    },
  });

  const generate = (data: GenerateMealRecommendationRequest = {}) => {
    generateMutation.mutate(date ? { ...data, date } : data);
  };

  return {
    // アクション
    generate,

    // 状態
    isGenerating: generateMutation.isPending,
    generateError: generateMutation.error,
  };
}
