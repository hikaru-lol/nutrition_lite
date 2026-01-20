// src/modules/meal/api/client.ts
import { apiFetch } from '@/shared/lib/api/fetcher';
import type {
  MealItemListResponse,
  MealItemRequest,
  MealItemResponse,
} from './types';

export const mealApi = {
  listByDate: (date: string) => {
    const qs = new URLSearchParams({ date });
    return apiFetch<MealItemListResponse>(`/meal-items?${qs.toString()}`);
  },

  create: (body: MealItemRequest) =>
    apiFetch<MealItemResponse>('/meal-items', { method: 'POST', body }),

  update: (entryId: string, body: MealItemRequest) =>
    apiFetch<MealItemResponse>(`/meal-items/${entryId}`, {
      method: 'PATCH',
      body,
    }),

  delete: (entryId: string) =>
    apiFetch<void>(`/meal-items/${entryId}`, { method: 'DELETE' }),
};
