/**
 * useTodayNutritionCalculator - Layer 4: Feature Hook
 *
 * データフロー:
 * 1. 目標取得 → 2. 食事取得 → 3. 栄養サマリー取得 → 4. 進捗計算 → 5. 状態判定
 *
 * 責務:
 * - 栄養進捗に必要なデータの取得・計算
 * - UI表示状態の判定
 */

import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTargetService } from '@/modules/target/services/targetService';
import { useNutritionService } from '@/modules/nutrition/services/nutritionService';
import { useMealService } from '@/modules/meal/services/mealService';
import { useNutritionProgressService } from '@/modules/nutrition-progress/services/nutritionProgressService';
import { useMealItemsByDate } from '@/modules/meal/hooks/mealOptimisticMutations';
import type { DailySummaryData } from '@/modules/nutrition-progress/services/nutritionProgressService';
import type { NutrientProgress } from '../contract/todayContract';
import type { Target } from '@/modules/target/contract/targetContract';

export type { NutrientProgress };

// ========================================
// Types
// ========================================

export type NutritionProgressState =
  | 'no-target'   // 目標未設定
  | 'no-meals'    // 食事記録なし
  | 'loading'     // 取得中
  | 'error'       // エラー
  | 'success';    // 成功

interface UseTodayNutritionCalculatorProps {
  date: string; // YYYY-MM-DD
}

export interface TodayNutritionCalculatorModel {
  // Core Data
  activeTarget: Target | null;
  nutrientProgress: NutrientProgress[];
  dailySummaryData: DailySummaryData | null;
  progressState: NutritionProgressState;

  // Legacy State (後方互換性のため残す)
  isLoading: boolean;
  isError: boolean;
  isDailySummaryLoading: boolean;
  isDailySummaryError: boolean;

  // Actions
  refetchDailySummary: () => void;
}

// ========================================
// Hook Implementation
// ========================================

export function useTodayNutritionCalculator(
  props: UseTodayNutritionCalculatorProps
): TodayNutritionCalculatorModel {
  const { date } = props;

  // ========================================
  // Services (Layer 5)
  // ========================================

  const targetService = useTargetService();
  const nutritionService = useNutritionService();
  const mealService = useMealService();
  const nutritionProgressService = useNutritionProgressService();

  // ========================================
  // Data Fetching (依存順)
  // ========================================

  // 1. 目標取得
  const activeTargetQuery = useQuery({
    queryKey: ['targets', 'active'] as const,
    queryFn: () => targetService.getActiveTarget(),
    retry: false,
  });

  // 2. 食事取得
  const mealItemsQuery = useMealItemsByDate(date);

  // 3. 栄養計算用の最初の食事を特定
  const mealItems = mealItemsQuery.data?.items;
  const firstMealItem = useMemo(() => {
    if (!mealItems?.length) return null;
    return mealService.findFirstMealForNutrition(mealItems);
  }, [mealItems, mealService]);

  // 4. 日次栄養サマリー取得（目標 + 食事が揃ったら）
  const canFetchDailySummary =
    activeTargetQuery.isSuccess &&
    activeTargetQuery.data !== null &&
    mealItemsQuery.isSuccess &&
    firstMealItem !== null;

  const dailySummaryQuery = useQuery({
    queryKey: [
      'nutrition',
      'daily-summary',
      date,
      firstMealItem?.meal_type,
      firstMealItem?.meal_index
    ] as const,
    queryFn: () => nutritionService.getDailySummary(date, firstMealItem!),
    enabled: canFetchDailySummary,
    retry: false,
  });

  // ========================================
  // Computed Values
  // ========================================

  const activeTarget = activeTargetQuery.data ?? null;
  const mealItemsCount = mealItemsQuery.data?.items?.length ?? 0;

  // 進捗データ計算
  const progressData = useMemo(() => {
    const dailySummary = dailySummaryQuery.data ?? null;
    return nutritionProgressService.calculateProgressData(activeTarget, dailySummary);
  }, [activeTarget, dailySummaryQuery.data, nutritionProgressService]);

  // UI表示状態の判定
  const progressState = useMemo((): NutritionProgressState => {
    // 1. 目標未設定
    if (!activeTarget) return 'no-target';

    // 2. 食事記録なし
    if (mealItemsCount === 0) return 'no-meals';

    // 3. データ取得中
    if (activeTargetQuery.isLoading || dailySummaryQuery.isLoading) return 'loading';

    // 4. 真のエラー（activeTargetのエラーのみ）
    // dailySummaryQuery.isError は除外（栄養分析未生成の可能性があるため）
    if (activeTargetQuery.isError) return 'error';

    // 5. 成功（食事あり、栄養分析未生成でも0%表示）
    return 'success';
  }, [
    activeTarget,
    mealItemsCount,
    activeTargetQuery.isLoading,
    activeTargetQuery.isError,
    dailySummaryQuery.isLoading,
  ]);

  // ========================================
  // Return Model
  // ========================================

  return {
    // Core Data
    activeTarget,
    nutrientProgress: progressData.nutrientProgress,
    dailySummaryData: progressData.dailySummaryData,
    progressState,

    // Legacy State
    isLoading: activeTargetQuery.isLoading,
    isError: activeTargetQuery.isError,
    isDailySummaryLoading: dailySummaryQuery.isLoading,
    isDailySummaryError: dailySummaryQuery.isError,

    // Actions
    refetchDailySummary: () => dailySummaryQuery.refetch(),
  };
}
