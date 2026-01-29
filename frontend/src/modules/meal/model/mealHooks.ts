'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { MealItemRequest } from '../contract/mealContract';
import * as api from '../api/mealClient';

const qk = {
  byDate: (date: string) => ['meal-items', 'by-date', date] as const,
};

export function useMealItemsByDate(date: string) {
  return useQuery({
    queryKey: qk.byDate(date),
    queryFn: () => api.fetchMealItemsByDate(date),
  });
}

export function useCreateMealItem(date: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (req: MealItemRequest) => api.createMealItem(req),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: qk.byDate(date) });
    },
  });
}

export function useDeleteMealItem(date: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (entryId: string) => api.deleteMealItem(entryId),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: qk.byDate(date) });
    },
  });
}
