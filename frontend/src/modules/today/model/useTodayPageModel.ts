'use client';

import { useQueries } from '@tanstack/react-query';
import type { MealItemRequest } from '@/modules/meal/contract/mealContract';
import { useTodayNutritionCalculator, type TodayNutritionCalculatorModel } from '../hooks/useTodayNutritionCalculator';
import { useMealManager, type MealManagerModel, useMealCompletionCalculator, type MealCompletionCalculatorModel } from '@/modules/meal';
import { useProfileManager, type ProfileManagerModel } from '@/modules/profile';
import { useTargetManager, type TargetManagerModel } from '@/modules/target';
import { useDailyReportManager, type DailyReportManagerModel } from '../hooks/useDailyReportManager';
import { useNutritionAnalysisState, type NutritionAnalysisStateModel } from '../ui/hooks/useNutritionAnalysisState';
import { useMealSectionState, type MealSectionStateManager } from '../hooks/useMealSectionState';

export type TodayMealItemFormValues = MealItemRequest;

interface UseTodayPageModelProps {
  date: string;
}

export function useTodayPageModel(props: UseTodayPageModelProps) {
  const { date } = props;

  // Layer 4: Feature Hooks
  const nutritionCalculator: TodayNutritionCalculatorModel = useTodayNutritionCalculator({ date });
  const mealManager: MealManagerModel = useMealManager({ date });
  const profileManager: ProfileManagerModel = useProfileManager();
  const targetManager: TargetManagerModel = useTargetManager();
  const dailyReportManager: DailyReportManagerModel = useDailyReportManager({
    date,
    enabled: mealManager.mealItemsQuery.isSuccess,
  });
  const mealCompletionCalculator: MealCompletionCalculatorModel = useMealCompletionCalculator({
    meals: mealManager.mealItems,
    profile: profileManager.profile,
  });
  const mealSectionState: MealSectionStateManager = useMealSectionState(date, {
    autoLoad: true,
    meals: mealManager.mealItems,
    mealsPerDay: profileManager.profile?.meals_per_day ?? 3,
  });

  // Layer 2: UI Orchestration
  const nutritionAnalysisState: NutritionAnalysisStateModel = useNutritionAnalysisState({ date });

  // Aggregated States - ページ初期表示用の基本データ状態
  const isPageLoading = nutritionCalculator.isLoading || mealManager.isLoading;
  const isPageError = nutritionCalculator.isError || mealManager.isError;

  // Layer 3: 各食事セクションの栄養データ有無を集約
  const mealsPerDay = profileManager.profile?.meals_per_day ?? 3;

  // キャッシュ状態をリアクティブに監視（enabled: false なのでリクエストは投げない）
  const nutritionCacheQueries = useQueries({
    queries: [
      // メイン食事（食事1, 食事2, ...）
      ...Array.from({ length: mealsPerDay }, (_, i) => ({
        queryKey: ['nutrition', 'meal-section', date, 'main', i + 1] as const,
        enabled: false, // キャッシュ監視のみ、リクエストは投げない
      })),
      // 間食
      {
        queryKey: ['nutrition', 'meal-section', date, 'snack', null] as const,
        enabled: false,
      },
    ],
  });

  // キャッシュの状態から nutritionDataAvailability を構築（リアクティブに更新される）
  const nutritionDataAvailability = new Map<string, boolean>();

  // メイン食事
  for (let i = 0; i < mealsPerDay; i++) {
    const key = `main-${i + 1}`;
    nutritionDataAvailability.set(key, nutritionCacheQueries[i].data !== undefined);
  }

  // 間食
  nutritionDataAvailability.set(
    'snack',
    nutritionCacheQueries[mealsPerDay].data !== undefined
  );

  return {
    isPageLoading,
    isPageError,
    nutritionCalculator,
    mealManager,
    profileManager,
    targetManager,
    dailyReportManager,
    nutritionAnalysisState,
    mealCompletionCalculator,
    mealSectionState,
    nutritionDataAvailability,
  };
}
