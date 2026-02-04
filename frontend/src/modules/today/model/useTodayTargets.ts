/**
 * useTodayTargets - 目標管理専用フック
 *
 * 責務:
 * - アクティブな目標の取得
 * - 栄養素進捗の計算
 * - 日次サマリーデータの管理
 */

'use client';

import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';

import { todayQueryKeys } from '../lib/queryKeys';
import type {
  TodayTargetsModel,
  NutrientProgress,
} from '../types/todayTypes';
import {
  nutrientLabels,
  formatLocalDateYYYYMMDD,
} from '../types/todayTypes';
import { fetchActiveTarget } from '@/modules/target/api/targetClient';
import {
  getNutritionData,
  computeNutritionData,
} from '@/modules/nutrition/api/nutritionClient';
import type {
  DailyNutritionSummary,
} from '@/modules/nutrition/contract/nutritionContract';

// ========================================
// Props Interface
// ========================================

interface UseTodayTargetsProps {
  date?: string; // YYYY-MM-DD format
}

// ========================================
// Main Hook
// ========================================

export function useTodayTargets(props: UseTodayTargetsProps = {}): TodayTargetsModel {
  // 日付の正規化
  const date = useMemo(() => {
    return props.date || formatLocalDateYYYYMMDD(new Date());
  }, [props.date]);

  // ========================================
  // Data Fetching
  // ========================================

  // アクティブな目標の取得
  const activeTargetQuery = useQuery({
    queryKey: todayQueryKeys.activeTarget(),
    queryFn: fetchActiveTarget,
    retry: false,
  });

  // 日次栄養サマリーの取得
  const dailySummaryQuery = useQuery({
    queryKey: todayQueryKeys.dailySummary(date),
    queryFn: () => getNutritionData({ date }),
    enabled: activeTargetQuery.isSuccess && !!activeTargetQuery.data,
    retry: false,
  });

  // ========================================
  // Computed Values
  // ========================================

  // 栄養素進捗の計算
  const nutrientProgress: NutrientProgress[] = useMemo(() => {
    const target = activeTargetQuery.data;
    if (!target) return [];

    const dailySummary: DailyNutritionSummary | null =
      dailySummaryQuery.data?.daily ?? null;

    return target.nutrients.map((t) => {
      const actual = dailySummary?.nutrients.find((n) => n.code === t.code);
      const actualAmount = actual?.value ?? 0;
      const percentage = t.amount > 0 ? (actualAmount / t.amount) * 100 : 0;

      return {
        code: t.code,
        label: nutrientLabels[t.code],
        target: t.amount,
        actual: actualAmount,
        unit: t.unit,
        percentage,
      };
    });
  }, [activeTargetQuery.data, dailySummaryQuery.data]);

  // 日次サマリーデータ（カロリー + PFC）
  const dailySummaryData = useMemo(() => {
    const target = activeTargetQuery.data;
    if (!target) return null;

    const dailySummary: DailyNutritionSummary | null =
      dailySummaryQuery.data?.daily ?? null;

    // PFC情報を取得
    const proteinTarget = target.nutrients.find(n => n.code === 'protein');
    const proteinActual = dailySummary?.nutrients.find(n => n.code === 'protein');

    const fatTarget = target.nutrients.find(n => n.code === 'fat');
    const fatActual = dailySummary?.nutrients.find(n => n.code === 'fat');

    const carbohydrateTarget = target.nutrients.find(n => n.code === 'carbohydrate');
    const carbohydrateActual = dailySummary?.nutrients.find(n => n.code === 'carbohydrate');

    // カロリーは PFC から計算（タンパク質・炭水化物: 4kcal/g, 脂質: 9kcal/g）
    const currentCalories =
      ((proteinActual?.value ?? 0) * 4) +
      ((fatActual?.value ?? 0) * 9) +
      ((carbohydrateActual?.value ?? 0) * 4);

    const targetCalories =
      ((proteinTarget?.amount ?? 0) * 4) +
      ((fatTarget?.amount ?? 0) * 9) +
      ((carbohydrateTarget?.amount ?? 0) * 4);

    return {
      currentCalories: Math.round(currentCalories),
      targetCalories: Math.round(targetCalories),
      protein: {
        current: proteinActual?.value ?? 0,
        target: proteinTarget?.amount ?? 0,
        percentage: proteinTarget?.amount ?
          ((proteinActual?.value ?? 0) / proteinTarget.amount) * 100 : 0,
      },
      fat: {
        current: fatActual?.value ?? 0,
        target: fatTarget?.amount ?? 0,
        percentage: fatTarget?.amount ?
          ((fatActual?.value ?? 0) / fatTarget.amount) * 100 : 0,
      },
      carbohydrate: {
        current: carbohydrateActual?.value ?? 0,
        target: carbohydrateTarget?.amount ?? 0,
        percentage: carbohydrateTarget?.amount ?
          ((carbohydrateActual?.value ?? 0) / carbohydrateTarget.amount) * 100 : 0,
      },
    };
  }, [activeTargetQuery.data, dailySummaryQuery.data]);

  // ========================================
  // Actions Implementation
  // ========================================

  const refetchDailySummary = () => {
    dailySummaryQuery.refetch();
  };

  // ========================================
  // Return Value
  // ========================================

  return {
    // State
    activeTarget: activeTargetQuery.data ?? null,
    nutrientProgress,
    dailySummaryData,
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
export function useTodayNutrientProgress(props: UseTodayTargetsProps = {}) {
  const { nutrientProgress, isLoading, isError } = useTodayTargets(props);

  return {
    progress: nutrientProgress,
    isLoading,
    isError,
  };
}

// ========================================
// ヘルパー関数
// ========================================

/**
 * 栄養素達成率の色を取得
 */
export function getNutrientProgressColor(percentage: number): string {
  if (percentage >= 100) return 'text-red-500';   // 100%以上は赤（過剰）
  if (percentage >= 80) return 'text-green-500';  // 80-100%は緑（良好）
  if (percentage >= 50) return 'text-yellow-500'; // 50-80%は黄（注意）
  return 'text-gray-500';                          // 50%未満は灰（不足）
}

/**
 * 栄養素達成率のプログレスバー色を取得
 */
export function getNutrientProgressBarColor(percentage: number): string {
  if (percentage >= 100) return 'bg-red-500';
  if (percentage >= 80) return 'bg-green-500';
  return 'bg-blue-500';
}