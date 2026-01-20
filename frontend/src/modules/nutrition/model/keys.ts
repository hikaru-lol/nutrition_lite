// src/modules/nutrition/model/keys.ts
import type { MealType } from '../api/types';

export const nutritionKeys = {
  all: ['nutrition'] as const,

  daily: (date: string) => [...nutritionKeys.all, 'daily', date] as const,

  meal: (args: {
    date: string;
    meal_type: MealType;
    meal_index?: number | null;
  }) =>
    [
      ...nutritionKeys.all,
      'meal',
      args.date,
      args.meal_type,
      args.meal_type === 'main' ? String(args.meal_index ?? '') : 'snack',
    ] as const,
};
