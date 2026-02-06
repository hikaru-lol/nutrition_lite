'use client';

import { useMemo } from 'react';
import type { MealItemRequest, MealType } from '@/modules/meal/contract/mealContract';
import { useTodayNutritionProgress, type TodayNutritionProgressModel } from '../hooks/useTodayNutritionProgress';
import { useMealManagement, type MealManagementModel, useMealCompletionStatus, type MealCompletionStatusModel } from '@/modules/meal';
import { useProfileManagement, type ProfileManagementModel } from '@/modules/profile';
import { useTargetManagement, type TargetManagementModel } from '@/modules/target';
import { useDailyReportManagement, type DailyReportManagementModel } from '../hooks/useDailyReportManagement';
import { useNutritionAnalysisState, type NutritionAnalysisStateModel } from '../ui/hooks/useNutritionAnalysisState';

// ========================================
// Types
// ========================================

export type TodayMealItemFormValues = MealItemRequest;

interface UseTodayPageModelProps {
  date?: string;
}

// ========================================
// Helpers
// ========================================

function formatLocalDateYYYYMMDD(d: Date): string {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

// ========================================
// Hook
// ========================================

export function useTodayPageModel(props: UseTodayPageModelProps = {}) {
  const date = useMemo(() => {
    return props.date || formatLocalDateYYYYMMDD(new Date());
  }, [props.date]);

  // Layer 4: Feature Hooks
  const nutrition: TodayNutritionProgressModel = useTodayNutritionProgress({ date });
  const meals: MealManagementModel = useMealManagement({ date });
  const profile: ProfileManagementModel = useProfileManagement();
  const targets: TargetManagementModel = useTargetManagement();
  const dailyReport: DailyReportManagementModel = useDailyReportManagement({
    date,
    enabled: meals.mealItemsQuery.isSuccess,
  });
  const mealCompletion: MealCompletionStatusModel = useMealCompletionStatus({
    meals: meals.mealItems,
    profile: profile.profile,
  });

  // Layer 2: UI Orchestration
  const nutritionAnalysis: NutritionAnalysisStateModel = useNutritionAnalysisState({ date });

  // Aggregated States
  const isLoading = nutrition.isLoading || meals.isLoading;
  const isError = nutrition.isError || meals.isError;


  return {
    date,
    isLoading,
    isError,
    nutrition,
    meals,
    profile,
    targets,
    dailyReport,
    nutritionAnalysis,
    mealCompletion,
  };
}
