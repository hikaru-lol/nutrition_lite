/**
 * useMealCompletionStatus - Layer 4: Feature Logic
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

export interface MealCompletionStatusModel {
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

interface UseMealCompletionStatusProps {
  meals: readonly MealItem[];
  profile: Profile | null | undefined;
}

export function useMealCompletionStatus({
  meals,
  profile,
}: UseMealCompletionStatusProps): MealCompletionStatusModel {

  const mainMealCount = useMemo(() => {
    return meals.filter(item => item.meal_type === 'main').length;
  }, [meals]);

  const requiredMeals = profile?.meals_per_day ?? 3;

  const isValid = useMemo(() => {
    if (!profile?.meals_per_day) return false;
    return mainMealCount >= profile.meals_per_day;
  }, [profile, mainMealCount]);

  const status = useMemo((): MealCompletionStatus => {
    return {
      completed: mainMealCount,
      required: requiredMeals,
    };
  }, [mainMealCount, requiredMeals]);

  const missingCount = useMemo(() => {
    return Math.max(0, requiredMeals - mainMealCount);
  }, [requiredMeals, mainMealCount]);

  const hasEnoughData = useMemo(() => {
    if (!profile) return false;
    return mainMealCount >= requiredMeals;
  }, [profile, mainMealCount, requiredMeals]);

  return {
    isValid,
    status,
    missingCount,
    hasEnoughData,
  };
}
