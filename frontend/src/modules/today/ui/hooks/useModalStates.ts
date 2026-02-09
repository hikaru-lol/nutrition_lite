/**
 * useModalStates - モーダル状態の統合管理
 *
 * Layer 2: UI Orchestration
 *
 * 責務:
 * - 全モーダルの状態を一元管理
 * - TodayPageContentから簡単にアクセス可能
 */

import { useAddMealModalState } from './useAddMealModalState';
import { useEditMealModalState } from './useEditMealModalState';
import { useMealRecommendationModalState } from './useMealRecommendationModalState';
import { useNutritionAnalysisModalState } from './useNutritionAnalysisModalState';

// ========================================
// Types
// ========================================

export interface ModalStates {
  addMeal: ReturnType<typeof useAddMealModalState>;
  editMeal: ReturnType<typeof useEditMealModalState>;
  mealRecommendation: ReturnType<typeof useMealRecommendationModalState>;
  nutritionAnalysis: ReturnType<typeof useNutritionAnalysisModalState>;
}

// ========================================
// Hook Implementation
// ========================================

/**
 * 全モーダル状態を統合
 *
 * 将来的に：
 * - モーダル間の相互作用の管理
 * - グローバルモーダル状態の管理
 */
export function useModalStates(): ModalStates {
  const addMeal = useAddMealModalState();
  const editMeal = useEditMealModalState();
  const mealRecommendation = useMealRecommendationModalState();
  const nutritionAnalysis = useNutritionAnalysisModalState();

  return {
    addMeal,
    editMeal,
    mealRecommendation,
    nutritionAnalysis,
  };
}
