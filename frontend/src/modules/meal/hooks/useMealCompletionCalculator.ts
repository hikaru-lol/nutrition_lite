/**
 * useMealCompletionCalculator - Layer 4: Feature Logic
 *
 * 食事完了状態の判定ロジック
 *
 * 責務:
 * - 食事完了の判定
 * - 完了状態の計算
 * - 不足食事数の計算
 * - データ充足性の判定
 */

'use client';

import { useMemo } from 'react';
import type { MealItem } from '@/modules/meal/contract/mealContract';
import type { Profile } from '@/modules/profile/contract/profileContract';

// ========================================
// Types
// ========================================

export interface MealCompletionStatus {
  completed: number;
  required: number;
}

export interface MealCompletionCalculatorModel {
  /** 食事記録が必要数に達しているか */
  isValid: boolean;

  /** 完了状態 */
  status: MealCompletionStatus;

  /** 不足している食事数 */
  missingCount: number;

  /** 十分なデータがあるか */
  hasEnoughData: boolean;
}

// ========================================
// Hook Implementation
// ========================================

interface UseMealCompletionCalculatorProps {
  meals: readonly MealItem[];
  profile: Profile | null | undefined;
}

export function useMealCompletionCalculator({
  meals,
  profile,
}: UseMealCompletionCalculatorProps): MealCompletionCalculatorModel {

  // 記録されている食事回数をカウント（品目数ではなく、各meal_indexに最低1品目あればカウント）
  const completedMealCount = useMemo(() => {
    const mealIndexes = new Set(
      meals
        .filter(item => item.meal_type === 'main')
        .map(item => item.meal_index)
    );
    return mealIndexes.size;
  }, [meals]);

  const requiredMeals = profile?.meals_per_day ?? 3;

  const isValid = useMemo(() => {
    if (!profile?.meals_per_day) return false;
    return completedMealCount >= profile.meals_per_day;
  }, [profile, completedMealCount]);

  const status = useMemo((): MealCompletionStatus => {
    return {
      completed: completedMealCount,
      required: requiredMeals,
    };
  }, [completedMealCount, requiredMeals]);

  const missingCount = useMemo(() => {
    return Math.max(0, requiredMeals - completedMealCount);
  }, [requiredMeals, completedMealCount]);

  const hasEnoughData = useMemo(() => {
    if (!profile) return false;
    return completedMealCount >= requiredMeals;
  }, [profile, completedMealCount, requiredMeals]);

  return {
    isValid,
    status,
    missingCount,
    hasEnoughData,
  };
}
