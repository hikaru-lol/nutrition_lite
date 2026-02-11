/**
 * useMealRecommendationQuery - Layer 4: Feature Logic
 *
 * 食事提案のデータ取得を管理
 */

import { useQuery } from '@tanstack/react-query';
import { qk } from '@/shared/lib/query/keys';
import { mealRecommendationApi } from '../api/mealRecommendationClient';
import { is404Error } from '../lib/mealRecommendationHelpers';
import type { MealRecommendation } from '../contract/mealRecommendationContract';

// =============================================================================
// Types
// =============================================================================

export interface UseMealRecommendationQueryOptions {
  date?: string;  // YYYY-MM-DD
  enabled?: boolean;
}

export interface MealRecommendationQueryModel {
  // データ
  recommendation: MealRecommendation | null;
  recommendations: MealRecommendation[] | undefined;

  // 状態
  isLoading: boolean;
  isLoadingHistory: boolean;
  error: Error | null;

  // アクション
  refetch: () => void;
  loadHistory: () => void;
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useMealRecommendationQuery(
  options: UseMealRecommendationQueryOptions = {}
): MealRecommendationQueryModel {
  const { date, enabled = true } = options;

  // クエリ：特定日の食事提案取得
  const todayQuery = useQuery({
    queryKey: qk.mealRecommendation.byDate(date || 'today'),
    queryFn: async () => {
      if (!date) {
        // 日付が指定されていない場合はリストから最新を取得
        const listResponse = await mealRecommendationApi.list({ limit: 1 });
        return listResponse.recommendations[0] || null;
      }

      try {
        const response = await mealRecommendationApi.getByDate(date);
        return response.recommendation;
      } catch (error) {
        // 404の場合はnullを返す（未生成状態）
        if (is404Error(error)) {
          return null;
        }
        throw error;
      }
    },
    enabled,
    staleTime: 5 * 60 * 1000, // 5分間キャッシュ
  });

  // クエリ：食事提案リスト取得
  const listQuery = useQuery({
    queryKey: qk.mealRecommendation.list(10),
    queryFn: () => mealRecommendationApi.list({ limit: 10 }),
    enabled: false, // 手動でトリガー
    staleTime: 5 * 60 * 1000, // 5分間キャッシュ
  });

  return {
    // データ
    recommendation: todayQuery.data ?? null,
    recommendations: listQuery.data?.recommendations,

    // 状態
    isLoading: todayQuery.isLoading,
    isLoadingHistory: listQuery.isLoading,
    error: todayQuery.error,

    // アクション
    refetch: todayQuery.refetch,
    loadHistory: listQuery.refetch,
  };
}
