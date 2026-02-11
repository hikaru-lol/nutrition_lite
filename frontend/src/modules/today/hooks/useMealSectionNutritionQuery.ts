/**
 * useMealSectionNutritionQuery - Layer 4: Feature Logic
 *
 * 責務:
 * - 食事セクション毎の栄養データを useQuery で管理
 * - 自動的にキャッシュ更新時に再レンダリング
 * - サーバーから既存データを取得
 */

import { useQuery } from '@tanstack/react-query';
import { getNutritionData, computeNutritionData } from '@/modules/nutrition/api/nutritionClient';
import type { MealType } from '@/modules/meal/contract/mealContract';

interface UseMealSectionNutritionQueryProps {
  date: string;
  mealType: MealType;
  mealIndex?: number;
  enabled?: boolean;
}

export function useMealSectionNutritionQuery({
  date,
  mealType,
  mealIndex,
  enabled = true,
}: UseMealSectionNutritionQueryProps) {
  const queryKey = ['nutrition', 'meal-section', date, mealType, mealIndex ?? null] as const;

  // ✅ useQuery を使用 - キャッシュ更新時に自動的に再レンダリング
  const query = useQuery({
    queryKey,
    queryFn: async () => {
      try {
        // まず既存データを取得
        return await getNutritionData({
          date,
          meal_type: mealType,
          meal_index: mealIndex ?? null,
        });
      } catch (error) {
        // 404 の場合は null を返す（エラーにしない）
        if (error instanceof Error && error.message.includes('404')) {
          return null;
        }
        throw error;
      }
    },
    enabled,
    staleTime: 1000 * 60 * 30, // 30分
    retry: false, // 404 の場合はリトライしない
  });

  return {
    data: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    hasData: query.data !== null && query.data !== undefined,
  };
}
