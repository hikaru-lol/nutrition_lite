import { clientApiFetch } from '@/shared/api/client';
import {
  MealItemListResponseSchema,
  MealItemRequestSchema,
  MealItemResponseSchema,
  type MealItemListResponse,
  type MealItemRequest,
  type MealItemResponse,
} from '../contract/mealContract';

export async function fetchMealItemsByDate(
  date: string
): Promise<MealItemListResponse> {
  const raw = await clientApiFetch<unknown>(
    `/meal-items?date=${encodeURIComponent(date)}`,
    { method: 'GET' }
  );
  return MealItemListResponseSchema.parse(raw);
}

export async function createMealItem(
  input: MealItemRequest
): Promise<MealItemResponse> {
  const safe = MealItemRequestSchema.parse(input);
  const raw = await clientApiFetch<unknown>(`/meal-items`, {
    method: 'POST',
    body: safe,
  });
  return MealItemResponseSchema.parse(raw);
}

export async function updateMealItem(
  entryId: string,
  input: MealItemRequest
): Promise<MealItemResponse> {
  const safe = MealItemRequestSchema.parse(input);
  const raw = await clientApiFetch<unknown>(`/meal-items/${entryId}`, {
    method: 'PATCH',
    body: safe,
  });
  return MealItemResponseSchema.parse(raw);
}

export async function deleteMealItem(entryId: string): Promise<void> {
  await clientApiFetch<unknown>(`/meal-items/${entryId}`, { method: 'DELETE' });
}
