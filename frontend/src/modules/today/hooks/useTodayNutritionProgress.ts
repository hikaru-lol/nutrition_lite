/**
 * useTodayNutritionProgress - Layer 4: Feature Hook
 *
 * 責務:
 * - React Query状態管理
 * - 非同期データ取得の統合
 * - UI向けデータの提供
 *
 * レイヤードアーキテクチャのFeature Logic層
 */

'use client';

import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';

import { useTargetService } from '@/modules/target/services/targetService';
import { useNutritionService } from '@/modules/nutrition/services/nutritionService';
import { useMealService } from '@/modules/meal/services/mealService';
import { useNutritionProgressService } from '@/modules/nutrition-progress/services/nutritionProgressService';
import type { DailySummaryData } from '@/modules/nutrition-progress/services/nutritionProgressService';
import { useMealItemsByDate } from '@/modules/meal/model/mealHooks';
import { formatLocalDateYYYYMMDD } from '../types/todayTypes';
import type { NutrientProgress } from '../types/todayTypes';

// ========================================
// Re-export Types
// ========================================

export type { NutrientProgress };

// ========================================
// Types
// ========================================

interface UseTodayNutritionProgressProps {
  date?: string; // YYYY-MM-DD format
}


export interface TodayNutritionProgressModel {
  // Data
  activeTarget: any | null;
  nutrientProgress: NutrientProgress[];
  dailySummaryData: DailySummaryData | null;

  // State
  isLoading: boolean;
  isError: boolean;
  isDailySummaryLoading: boolean;
  isDailySummaryError: boolean;

  // Actions
  refetchDailySummary: () => void;
}

// ========================================
// Main Hook
// ========================================

export function useTodayNutritionProgress(
  props: UseTodayNutritionProgressProps = {}
): TodayNutritionProgressModel {

  // Layer 5: Domain Service注入
  const targetService = useTargetService();
  const nutritionService = useNutritionService();
  const mealService = useMealService();
  const nutritionProgressService = useNutritionProgressService();

  // 日付の正規化
  const date = useMemo(() => {
    return props.date || formatLocalDateYYYYMMDD(new Date());
  }, [props.date]);

  // ========================================
  // Data Fetching (React Query管理)
  // ========================================

  // アクティブな目標の取得
  const activeTargetQuery = useQuery({
    queryKey: ['targets', 'active'] as const,
    queryFn: () => targetService.getActiveTarget(),
    retry: false,
  });

  // 食事データ取得（日次サマリー取得のために必要）
  const mealItemsQuery = useMealItemsByDate(date);

  // 最初の食事を特定（栄養分析用）
  const firstMealItem = useMemo(() => {
    if (!mealItemsQuery.data?.items?.length) return null;
    return mealService.findFirstMealForNutrition(mealItemsQuery.data.items);
  }, [mealItemsQuery.data?.items, mealService]);

  // 日次栄養サマリーの取得
  const dailySummaryQuery = useQuery({
    queryKey: [
      'nutrition',
      'daily-summary',
      date,
      firstMealItem?.meal_type,
      firstMealItem?.meal_index
    ] as const,
    queryFn: () => {
      if (!firstMealItem) throw new Error('No meals found');
      return nutritionService.getDailySummary(date, firstMealItem);
    },
    enabled:
      activeTargetQuery.isSuccess &&
      firstMealItem !== null &&
      activeTargetQuery.data !== null &&
      mealItemsQuery.isSuccess,
    retry: false,
  });

  // ========================================
  // Business Logic Computation (Layer 5統合)
  // ========================================

  // 栄養進捗データの統合計算
  const nutritionProgressData = useMemo(() => {
    const target = activeTargetQuery.data ?? null;
    const dailySummary = dailySummaryQuery.data ?? null;

    return nutritionProgressService.calculateProgressData(target, dailySummary);
  }, [
    activeTargetQuery.data,
    dailySummaryQuery.data,
    nutritionProgressService
  ]);

  // UI向けデータの分解
  const nutrientProgress: NutrientProgress[] = nutritionProgressData.nutrientProgress;
  const dailySummaryData: DailySummaryData = nutritionProgressData.dailySummaryData;

  // ========================================
  // Actions
  // ========================================

  const refetchDailySummary = () => {
    dailySummaryQuery.refetch();
  };

  // ========================================
  // Return Value
  // ========================================

  return {
    // Data
    activeTarget: activeTargetQuery.data ?? null,
    nutrientProgress,
    dailySummaryData,

    // State
    isLoading: activeTargetQuery.isLoading,
    isError: activeTargetQuery.isError,
    isDailySummaryLoading: dailySummaryQuery.isLoading,
    isDailySummaryError: dailySummaryQuery.isError,

    // Actions
    refetchDailySummary,
  };
}

// ========================================
// 軽量版Hook（進捗のみ）
// ========================================

/**
 * 栄養素進捗のみを取得する軽量フック
 */
export function useTodayNutrientProgressOnly(props: UseTodayNutritionProgressProps = {}) {
  const { nutrientProgress, isLoading, isError } = useTodayNutritionProgress(props);

  return {
    progress: nutrientProgress,
    isLoading,
    isError,
  };
}