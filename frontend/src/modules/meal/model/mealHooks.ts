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
    onMutate: async (newItem) => {
      // Cancel any outgoing refetches
      await qc.cancelQueries({ queryKey: qk.byDate(date) });

      // Snapshot the previous value
      const previousData = qc.getQueryData(qk.byDate(date));

      // Optimistically update to the new value with temporary ID
      qc.setQueryData(qk.byDate(date), (old: any) => {
        if (!old?.items) return { items: [{ ...newItem, id: `temp-${Date.now()}` }] };

        return {
          ...old,
          items: [...old.items, { ...newItem, id: `temp-${Date.now()}` }],
        };
      });

      return { previousData };
    },
    onError: (err, variables, context) => {
      if (context?.previousData) {
        qc.setQueryData(qk.byDate(date), context.previousData);
      }
    },
    onSettled: async () => {
      await qc.invalidateQueries({ queryKey: qk.byDate(date) });
    },
  });
}

export function useUpdateMealItem(date: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ entryId, data }: { entryId: string; data: MealItemRequest }) =>
      api.updateMealItem(entryId, data),
    onMutate: async ({ entryId, data }) => {
      // Cancel any outgoing refetches (so they don't overwrite our optimistic update)
      await qc.cancelQueries({ queryKey: qk.byDate(date) });

      // Snapshot the previous value
      const previousData = qc.getQueryData(qk.byDate(date));

      // Optimistically update to the new value
      qc.setQueryData(qk.byDate(date), (old: any) => {
        if (!old?.items) return old;

        return {
          ...old,
          items: old.items.map((item: any) =>
            item.id === entryId
              ? { ...item, ...data, id: entryId }
              : item
          ),
        };
      });

      // Return a context object with the snapshotted value
      return { previousData };
    },
    onError: (err, variables, context) => {
      // If the mutation fails, use the context returned from onMutate to roll back
      if (context?.previousData) {
        qc.setQueryData(qk.byDate(date), context.previousData);
      }
    },
    onSettled: async () => {
      // Always refetch after error or success to ensure we have the latest data
      await qc.invalidateQueries({ queryKey: qk.byDate(date) });
    },
  });
}

export function useDeleteMealItem(date: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (entryId: string) => api.deleteMealItem(entryId),
    onMutate: async (entryId) => {
      // Cancel any outgoing refetches
      await qc.cancelQueries({ queryKey: qk.byDate(date) });

      // Snapshot the previous value
      const previousData = qc.getQueryData(qk.byDate(date));

      // Optimistically remove the item
      qc.setQueryData(qk.byDate(date), (old: any) => {
        if (!old?.items) return old;

        return {
          ...old,
          items: old.items.filter((item: any) => item.id !== entryId),
        };
      });

      return { previousData };
    },
    onError: (err, variables, context) => {
      if (context?.previousData) {
        qc.setQueryData(qk.byDate(date), context.previousData);
      }
    },
    onSettled: async () => {
      await qc.invalidateQueries({ queryKey: qk.byDate(date) });
    },
  });
}
