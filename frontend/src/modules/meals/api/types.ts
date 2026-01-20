// src/modules/meal/api/types.ts

export type MealType = 'main' | 'snack';

export type MealItemRequest = {
  date: string; // YYYY-MM-DD
  meal_type: MealType;
  meal_index?: number | null; // main: 1..N, snack: null
  name: string;

  amount_value?: number | null;
  amount_unit?: string | null;

  serving_count?: number | null;
  note?: string | null;
};

export type MealItemResponse = MealItemRequest & {
  id: string; // uuid
};

export type MealItemListResponse = {
  items: MealItemResponse[];
};
