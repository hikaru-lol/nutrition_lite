// frontend/lib/api/meals.ts
import { apiGet, apiPost, apiPatch, apiDelete } from './client';

export type MealType = 'main' | 'snack';

export type MealItemResponse = {
  id: string;
  date: string; // "YYYY-MM-DD"
  meal_type: MealType;
  meal_index: number | null; // main: 1..N, snack: null
  name: string;
  amount_value: number | null;
  amount_unit: string | null;
  serving_count: number | null;
  note: string | null;
};

export type MealItemListResponse = {
  items: MealItemResponse[];
};

export async function fetchMealItems(
  date: string
): Promise<MealItemResponse[]> {
  const res = await apiGet<MealItemListResponse>(
    `/meal-items?date=${encodeURIComponent(date)}`
  );
  return res.items;
}

// 将来的に使うかもしれないので CRUD も用意（今すぐ使わなくてもOK）
export async function createMealItem(input: {
  date: string;
  meal_type: MealType;
  meal_index: number | null;
  name: string;
  amount_value?: number | null;
  amount_unit?: string | null;
  serving_count?: number | null;
  note?: string | null;
}): Promise<MealItemResponse> {
  return apiPost<MealItemResponse>('/meal-items', input);
}

export async function updateMealItem(
  id: string,
  input: {
    date: string;
    meal_type: MealType;
    meal_index: number | null;
    name: string;
    amount_value?: number | null;
    amount_unit?: string | null;
    serving_count?: number | null;
    note?: string | null;
  }
): Promise<MealItemResponse> {
  return apiPatch<MealItemResponse>(`/meal-items/${id}`, input);
}

export async function deleteMealItem(id: string): Promise<void> {
  await apiDelete<void>(`/meal-items/${id}`);
}
