/**
 * useNutritionAnalysisState - Layer 2: UI Orchestration
 *
 * 栄養分析モーダルの状態管理
 *
 * 責務:
 * - 栄養分析対象の食事選択状態管理
 * - 選択された食事の栄養データ取得
 * - モーダル開閉制御
 *
 * 移行元: useTodayPageModel.ts の以下の機能
 * - selectedMealForNutrition state
 * - selectMealForNutrition function
 * - clearSelectedMeal function
 * - selectedMealNutritionQuery
 */

'use client';

import { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { computeNutritionData } from '@/modules/nutrition/api/nutritionClient';
import type { MealType } from '@/modules/meal/contract/mealContract';

// ========================================
// Types
// ========================================

export interface SelectedMealForNutrition {
  meal_type: MealType;
  meal_index: number | null;
}

export interface NutritionAnalysisStateModel {
  // 選択状態
  selectedMealForNutrition: SelectedMealForNutrition | null;

  // 栄養データ
  nutritionData: Awaited<ReturnType<typeof computeNutritionData>> | undefined;
  isLoadingNutrition: boolean;
  isErrorNutrition: boolean;
  nutritionError: Error | null;

  // アクション
  selectMealForNutrition: (meal_type: MealType, meal_index: number | null) => void;
  clearSelectedMeal: () => void;
  refetchNutrition: () => void;
}

// ========================================
// Hook Implementation
// ========================================

interface UseNutritionAnalysisStateProps {
  date: string;
}

export function useNutritionAnalysisState({
  date,
}: UseNutritionAnalysisStateProps): NutritionAnalysisStateModel {
  // ========================================
  // State: 選択された食事
  // ========================================

  const [selectedMealForNutrition, setSelectedMealForNutrition] = useState<SelectedMealForNutrition | null>(null);

  // ========================================
  // Query: 選択された食事の栄養分析データ
  // ========================================

  const selectedMealNutritionQuery = useQuery({
    queryKey: [
      'nutrition',
      'selected-meal',
      date,
      selectedMealForNutrition?.meal_type,
      selectedMealForNutrition?.meal_index,
    ] as const,
    queryFn: async () => {
      if (!selectedMealForNutrition) {
        throw new Error('No meal selected for nutrition analysis');
      }
      return computeNutritionData({
        date,
        meal_type: selectedMealForNutrition.meal_type,
        meal_index: selectedMealForNutrition.meal_index,
      });
    },
    enabled: selectedMealForNutrition !== null,
    retry: false,
  });

  // ========================================
  // Actions
  // ========================================

  const selectMealForNutrition = useCallback((meal_type: MealType, meal_index: number | null) => {
    setSelectedMealForNutrition({ meal_type, meal_index });
  }, []);

  const clearSelectedMeal = useCallback(() => {
    setSelectedMealForNutrition(null);
  }, []);

  // ========================================
  // Return Model
  // ========================================

  return {
    // 選択状態
    selectedMealForNutrition,

    // 栄養データ
    nutritionData: selectedMealNutritionQuery.data,
    isLoadingNutrition: selectedMealNutritionQuery.isLoading,
    isErrorNutrition: selectedMealNutritionQuery.isError,
    nutritionError: selectedMealNutritionQuery.error,

    // アクション
    selectMealForNutrition,
    clearSelectedMeal,
    refetchNutrition: selectedMealNutritionQuery.refetch,
  };
}