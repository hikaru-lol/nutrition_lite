/**
 * useMealSectionState - Layer 4: Feature Logic
 *
 * 責務:
 * - 食事セクション毎の栄養データ管理
 * - キャッシュ管理
 * - サーバーからのデータ取得
 * - 初回ロード時の自動取得（オプション）
 */

import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useNutritionService } from '@/modules/nutrition/services/nutritionService';
import { getNutritionData } from '@/modules/nutrition/api/nutritionClient';
import type { MealType, MealItem } from '@/modules/meal/contract/mealContract';

export interface MealSectionStateManager {
  fetchNutrition: (mealType: MealType, mealIndex?: number) => Promise<any>;
  getFromCache: (mealType: MealType, mealIndex?: number) => any;
  getFromServer: (mealType: MealType, mealIndex?: number) => Promise<any | null>;
  hasCache: (mealType: MealType, mealIndex?: number) => boolean;
}

export interface UseMealSectionStateOptions {
  /** 初回ロード時に自動的にサーバーからデータを取得するか */
  autoLoad?: boolean;
  /** 食事アイテム一覧（autoLoad時に必要） */
  meals?: readonly MealItem[];
  /** 1日の食事回数（autoLoad時に必要） */
  mealsPerDay?: number;
}

export function useMealSectionState(
  date: string,
  options?: UseMealSectionStateOptions
): MealSectionStateManager {
  const queryClient = useQueryClient();
  const nutritionService = useNutritionService();

  const getQueryKey = (mealType: MealType, mealIndex?: number) => {
    return ['nutrition', 'meal-section', date, mealType, mealIndex ?? null] as const;
  };

  const fetchNutrition = async (mealType: MealType, mealIndex?: number) => {
    const queryKey = getQueryKey(mealType, mealIndex);

    const result = await queryClient.fetchQuery({
      queryKey,
      queryFn: () => nutritionService.fetchMealNutrition(date, mealType, mealIndex),
      staleTime: 1000 * 60 * 30,
    });

    return result;
  };

  const getFromCache = (mealType: MealType, mealIndex?: number) => {
    const queryKey = getQueryKey(mealType, mealIndex);
    return queryClient.getQueryData(queryKey);
  };

  const getFromServer = async (mealType: MealType, mealIndex?: number): Promise<any | null> => {
    const queryKey = getQueryKey(mealType, mealIndex);

    try {
      const result = await queryClient.fetchQuery({
        queryKey,
        queryFn: () => getNutritionData({
          date,
          meal_type: mealType,
          meal_index: mealIndex ?? null,
        }),
        staleTime: 1000 * 60 * 30,
      });
      return result;
    } catch (error) {
      return null;
    }
  };

  const hasCache = (mealType: MealType, mealIndex?: number) => {
    return getFromCache(mealType, mealIndex) !== undefined;
  };

  // 自動ロード: 初回マウント時に既存データをサーバーから取得
  useEffect(() => {
    if (!options?.autoLoad || !options.meals || !options.mealsPerDay) {
      return;
    }

    // 型の絞り込みのために変数に代入
    const meals = options.meals;
    const mealsPerDay = options.mealsPerDay;

    const fetchAllNutritionData = async () => {
      const fetchPromises: Promise<any>[] = [];

      // メイン食事（食事1, 食事2, ...）
      for (let i = 1; i <= mealsPerDay; i++) {
        const hasMeals = meals.some(
          m => m.meal_type === 'main' && (m.meal_index ?? 1) === i
        );

        if (hasMeals) {
          fetchPromises.push(getFromServer('main', i));
        }
      }

      // 間食
      const hasSnacks = meals.some(m => m.meal_type === 'snack');
      if (hasSnacks) {
        fetchPromises.push(getFromServer('snack'));
      }

      // すべてのデータ取得が完了するまで待つ
      if (fetchPromises.length > 0) {
        await Promise.allSettled(fetchPromises);

        // 完了後、キャッシュを invalidate して再レンダリングをトリガー
        queryClient.invalidateQueries({
          queryKey: ['nutrition', 'meal-section', date],
        });
      }
    };

    fetchAllNutritionData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [date, options?.meals, options?.mealsPerDay]);

  return {
    fetchNutrition,
    getFromCache,
    getFromServer,
    hasCache,
  };
}
