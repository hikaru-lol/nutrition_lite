/**
 * useTodayNutrition - 栄養分析専用フック
 *
 * 責務:
 * - 食事別の栄養分析実行
 * - 栄養データキャッシュ管理
 * - 選択された食事の栄養分析状態管理
 */

'use client';

import { useState, useMemo, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { toast } from 'sonner';

import { todayQueryKeys } from '../lib/queryKeys';
import type {
  TodayNutritionModel,
  SelectedMeal,
  formatLocalDateYYYYMMDD,
} from '../types/todayTypes';
import type { MealType } from '@/modules/meal/contract/mealContract';
import { computeNutritionData } from '@/modules/nutrition/api/nutritionClient';

// ========================================
// Props Interface
// ========================================

interface UseTodayNutritionProps {
  date?: string; // YYYY-MM-DD format
}

// ========================================
// Main Hook
// ========================================

export function useTodayNutrition(props: UseTodayNutritionProps = {}): TodayNutritionModel {
  // 日付の正規化
  const date = useMemo(() => {
    return props.date || formatLocalDateYYYYMMDD(new Date());
  }, [props.date]);

  // ========================================
  // Local State
  // ========================================

  // 選択された食事（UI用）
  const [selectedMeal, setSelectedMeal] = useState<SelectedMeal | null>(null);

  // 栄養データキャッシュ（メモリベース）
  const [nutritionCache, setNutritionCache] = useState<Map<string, any>>(
    () => new Map()
  );

  // ========================================
  // Data Fetching
  // ========================================

  // 選択された食事の栄養分析
  const selectedMealNutritionQuery = useQuery({
    queryKey: todayQueryKeys.mealNutrition(
      date,
      selectedMeal?.meal_type ?? '',
      selectedMeal?.meal_index ?? undefined
    ),
    queryFn: async () => {
      if (!selectedMeal) {
        throw new Error('No meal selected for nutrition analysis');
      }
      return computeNutritionData({
        date,
        meal_type: selectedMeal.meal_type,
        meal_index: selectedMeal.meal_index,
      });
    },
    enabled: selectedMeal !== null,
    retry: false,
  });

  // ========================================
  // Cache Management
  // ========================================

  // キャッシュキー生成
  const generateCacheKey = useCallback((mealType: string, mealIndex?: number) => {
    return `${date}-${mealType}-${mealIndex ?? 'null'}`;
  }, [date]);

  // キャッシュからデータ取得
  const getFromCache = useCallback((mealType: string, mealIndex?: number) => {
    const key = generateCacheKey(mealType, mealIndex);
    return nutritionCache.get(key) || null;
  }, [nutritionCache, generateCacheKey]);

  // キャッシュにデータ保存
  const saveToCache = useCallback((mealType: string, mealIndex: number | undefined, data: any) => {
    const key = generateCacheKey(mealType, mealIndex);
    setNutritionCache(prev => new Map(prev).set(key, data));
  }, [generateCacheKey]);

  // キャッシュクリア
  const clearNutritionCache = useCallback(() => {
    setNutritionCache(new Map());
  }, []);

  // ========================================
  // Actions Implementation
  // ========================================

  // 食事選択
  const selectMeal = useCallback((meal_type: MealType, meal_index: number | null) => {
    setSelectedMeal({ meal_type, meal_index });
  }, []);

  // 選択クリア
  const clearSelected = useCallback(() => {
    setSelectedMeal(null);
  }, []);

  // 栄養分析実行（キャッシュ機能付き）
  const analyze = useCallback(async (meal_type: MealType, meal_index?: number): Promise<any> => {
    try {
      // まずキャッシュをチェック
      const cachedData = getFromCache(meal_type, meal_index);
      if (cachedData) {
        console.log('栄養分析: キャッシュから取得', { meal_type, meal_index });
        return cachedData;
      }

      // キャッシュにない場合は新規取得
      console.log('栄養分析: 新規取得開始', { meal_type, meal_index });
      const nutritionData = await computeNutritionData({
        date,
        meal_type,
        meal_index: meal_index || null,
      });

      // キャッシュに保存
      saveToCache(meal_type, meal_index, nutritionData);

      toast.success('栄養分析が完了しました');
      return nutritionData;
    } catch (error) {
      console.error('栄養分析エラー:', error);
      toast.error('栄養分析に失敗しました');
      throw error;
    }
  }, [date, getFromCache, saveToCache]);

  // 再取得
  const refetch = useCallback(() => {
    if (selectedMeal) {
      // キャッシュから削除して再取得
      const key = generateCacheKey(selectedMeal.meal_type, selectedMeal.meal_index ?? undefined);
      setNutritionCache(prev => {
        const newCache = new Map(prev);
        newCache.delete(key);
        return newCache;
      });
      selectedMealNutritionQuery.refetch();
    }
  }, [selectedMeal, generateCacheKey, selectedMealNutritionQuery]);

  // 詳細表示（モーダル用）
  const showDetails = useCallback((data: any) => {
    // この関数は Context 経由でモーダル管理フックと連携する
    console.log('栄養詳細表示:', data);
  }, []);

  // ========================================
  // 選択された食事のデータをキャッシュと統合
  // ========================================

  const nutritionData = useMemo(() => {
    if (selectedMeal && selectedMealNutritionQuery.data) {
      // 新しいデータをキャッシュに保存
      saveToCache(
        selectedMeal.meal_type,
        selectedMeal.meal_index ?? undefined,
        selectedMealNutritionQuery.data
      );
      return selectedMealNutritionQuery.data;
    }
    return null;
  }, [selectedMeal, selectedMealNutritionQuery.data, saveToCache]);

  // ========================================
  // Return Value
  // ========================================

  return {
    // State
    selectedMeal,
    nutritionData,
    isLoading: selectedMealNutritionQuery.isLoading,
    isError: selectedMealNutritionQuery.isError,
    nutritionCache,

    // Actions
    selectMeal,
    clearSelected,
    analyze,
    getFromCache,
    refetch,
    showDetails,
  };
}

// ========================================
// 軽量版Hook（分析のみ）
// ========================================

/**
 * 栄養分析専用の軽量フック（UI状態管理なし）
 */
export function useMealNutritionAnalysis(props: UseTodayNutritionProps = {}) {
  const date = useMemo(() => {
    return props.date || formatLocalDateYYYYMMDD(new Date());
  }, [props.date]);

  // 栄養分析実行関数のみ提供
  const analyzeMeal = useCallback(async (meal_type: MealType, meal_index?: number) => {
    try {
      const result = await computeNutritionData({
        date,
        meal_type,
        meal_index: meal_index || null,
      });
      return result;
    } catch (error) {
      console.error('栄養分析エラー:', error);
      throw error;
    }
  }, [date]);

  return { analyzeMeal };
}

// ========================================
// ユーティリティ関数
// ========================================

/**
 * 栄養素の過不足を判定
 */
export function getNutrientStatus(actual: number, target: number): 'sufficient' | 'excess' | 'insufficient' {
  const percentage = target > 0 ? (actual / target) * 100 : 0;
  if (percentage >= 120) return 'excess';      // 120%以上は過剰
  if (percentage >= 80) return 'sufficient';   // 80-120%は適正
  return 'insufficient';                       // 80%未満は不足
}

/**
 * 栄養バランススコアを計算
 */
export function calculateNutritionScore(nutrients: Array<{ actual: number, target: number }>): number {
  if (nutrients.length === 0) return 0;

  const scores = nutrients.map(({ actual, target }) => {
    if (target === 0) return 1;
    const percentage = (actual / target) * 100;
    // 80-120%の範囲でスコアが高くなるように計算
    if (percentage >= 80 && percentage <= 120) return 1;
    if (percentage < 80) return percentage / 80;
    return Math.max(0, 1 - (percentage - 120) / 100);
  });

  return Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length * 100);
}