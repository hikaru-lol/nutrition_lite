// src/modules/nutrition/model/hooks.ts
'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { nutritionApi } from '../api/client';
import type { MealAndDailyNutritionResponse, MealType } from '../api/types';
import { nutritionKeys } from './keys';

/**
 * 栄養の再計算（meal + daily を返す）
 * - 成功時に meal と daily のキャッシュを set
 *
 * 注意：
 * - これは「再計算トリガー」なので useQuery ではなく useMutation が自然
 * - 画面側は「再計算」ボタンや、FoodEntry更新後に呼ぶ
 */
export function useRecomputeMealAndDailyNutrition() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (args: {
      date: string;
      meal_type: MealType;
      meal_index?: number | null;
    }) => nutritionApi.recomputeMealAndDaily(args),

    onSuccess: (res: MealAndDailyNutritionResponse, vars) => {
      // meal summary
      qc.setQueryData(nutritionKeys.meal(vars), res.meal);

      // daily summary
      qc.setQueryData(nutritionKeys.daily(res.daily.date), res.daily);
    },
  });
}
