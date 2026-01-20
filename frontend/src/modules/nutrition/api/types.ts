// src/modules/nutrition/api/types.ts

export type NutrientCode =
  | 'carbohydrate'
  | 'fat'
  | 'protein'
  | 'water'
  | 'fiber'
  | 'sodium'
  | 'iron'
  | 'calcium'
  | 'vitamin_d'
  | 'potassium';

export type NutrientSource = 'llm' | 'manual' | 'user_input' | 'aggregated';

export type MealType = 'main' | 'snack';

export type NutritionNutrientIntake = {
  code: NutrientCode;
  amount: number;
  unit: string;
  source: NutrientSource;
};

export type MealNutritionSummary = {
  id: string;
  date: string; // YYYY-MM-DD
  meal_type: MealType;
  meal_index: number | null;
  generated_at: string; // date-time
  nutrients: NutritionNutrientIntake[];
};

export type DailyNutritionSummary = {
  id: string;
  date: string; // YYYY-MM-DD
  generated_at: string; // date-time
  nutrients: NutritionNutrientIntake[];
};

export type MealAndDailyNutritionResponse = {
  meal: MealNutritionSummary;
  daily: DailyNutritionSummary;
};
