// frontend/lib/api/nutrition.ts
import { apiGet } from './client';
import type { MealType } from './meals';
import type { NutrientCode, NutrientSource } from './targets';

// Intake の1栄養素分
export type NutritionNutrientIntakeApi = {
  code: NutrientCode;
  amount: number;
  unit: string;
  source: NutrientSource;
};

// 1ミール分の栄養サマリ
export type MealNutritionSummaryApi = {
  id: string;
  date: string; // YYYY-MM-DD
  meal_type: MealType;
  meal_index: number | null;
  nutrients: NutritionNutrientIntakeApi[];
  generated_at: string;
};

// 1日分の栄養サマリ
export type DailyNutritionSummaryApi = {
  id: string;
  date: string; // YYYY-MM-DD
  nutrients: NutritionNutrientIntakeApi[];
  generated_at: string;
};

// /nutrition/meal のレスポンス
export type MealAndDailyNutritionResponse = {
  meal: MealNutritionSummaryApi;
  daily: DailyNutritionSummaryApi;
};

export type RecomputeMealNutritionParams = {
  date: string;
  mealType: MealType; // "main" | "snack"
  mealIndex?: number | null; // main のとき 1..N, snack のとき不要/undefined
};

export async function recomputeMealAndDailyNutrition(
  params: RecomputeMealNutritionParams
): Promise<MealAndDailyNutritionResponse> {
  const search = new URLSearchParams();
  search.set('date', params.date);
  search.set('meal_type', params.mealType);
  if (params.mealType === 'main' && params.mealIndex != null) {
    search.set('meal_index', String(params.mealIndex));
  }

  return apiGet<MealAndDailyNutritionResponse>(
    `/nutrition/meal?${search.toString()}`
  );
}
