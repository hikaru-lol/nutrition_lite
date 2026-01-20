// src/modules/nutrition/api/client.ts
import { apiFetch } from '@/shared/lib/api/fetcher';
import type { MealAndDailyNutritionResponse, MealType } from './types';

export const nutritionApi = {
  /**
   * GET /nutrition/meal?date=...&meal_type=...&meal_index=...
   * - main のとき meal_index 必須
   * - snack のとき meal_index は省略
   */
  recomputeMealAndDaily: (args: {
    date: string;
    meal_type: MealType;
    meal_index?: number | null;
  }) => {
    const qs = new URLSearchParams();
    qs.set('date', args.date);
    qs.set('meal_type', args.meal_type);

    if (args.meal_type === 'main') {
      if (args.meal_index == null) {
        throw new Error("meal_index is required when meal_type is 'main'");
      }
      qs.set('meal_index', String(args.meal_index));
    }

    return apiFetch<MealAndDailyNutritionResponse>(
      `/nutrition/meal?${qs.toString()}`
    );
  },
};
