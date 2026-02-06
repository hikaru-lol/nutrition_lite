/**
 * useMealManagement - Layer 4: Feature Logic
 *
 * 責務:
 * - 食事CRUD操作のReact Query統合
 * - 食事関連の非同期データフェッチング協調
 * - UI向けの食事データ統合
 */

'use client';

import { useMemo, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useMealService } from '../services/mealService';
import { useMealItemsByDate } from '../model/mealHooks';
import type { MealItem, MealItemRequest } from '../contract/mealContract';
import type { MealIdentifier, MealSection } from '../services/mealService';

// ========================================
// Types
// ========================================

interface UseMealManagementProps {
  date: string; // YYYY-MM-DD format
}

export interface MealManagementModel {
  // Data
  mealItems: readonly MealItem[];
  mealSections: readonly MealSection[];

  // Query state (for backward compatibility)
  mealItemsQuery: {
    isSuccess: boolean;
    isLoading: boolean;
    isError: boolean;
    error: Error | null;
    refetch: () => void;
  };

  // State
  isLoading: boolean;
  isError: boolean;
  error: Error | null;

  // CRUD Operations
  createMeal: (data: MealItemRequest) => Promise<MealItem>;
  updateMeal: (entryId: string, data: MealItemRequest) => Promise<MealItem>;
  deleteMeal: (entryId: string) => Promise<void>;

  // CRUD State
  createMutation: {
    isPending: boolean;
    isError: boolean;
    error: Error | null;
  };
  updateMutation: {
    isPending: boolean;
    isError: boolean;
    error: Error | null;
  };
  deleteMutation: {
    isPending: boolean;
    isError: boolean;
    error: Error | null;
  };
  isCreating: boolean;
  isUpdating: boolean;
  isDeleting: boolean;

  // Nutrition Analysis
  findFirstMealForNutrition: () => MealIdentifier | null;

  // Data Operations
  refetch: () => void;
  invalidate: () => void;
}

// ========================================
// Hook Implementation
// ========================================

export function useMealManagement({
  date,
}: UseMealManagementProps): MealManagementModel {

  // Layer 5 Service注入
  const mealService = useMealService();
  const queryClient = useQueryClient();

  // ========================================
  // Data Fetching
  // ========================================

  // 食事データ取得（既存フックを活用）
  const mealItemsQuery = useMealItemsByDate(date);

  // ========================================
  // CRUD Mutations
  // ========================================

  const createMutation = useMutation({
    mutationFn: (data: MealItemRequest) => mealService.createMealItem(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meal-items', date] });
    },
    onError: (error) => {
      console.error('Failed to create meal item:', error);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ entryId, data }: { entryId: string; data: MealItemRequest }) =>
      mealService.updateMealItem(entryId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meal-items', date] });
    },
    onError: (error) => {
      console.error('Failed to update meal item:', error);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (entryId: string) => mealService.deleteMealItem(entryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meal-items', date] });
    },
    onError: (error) => {
      console.error('Failed to delete meal item:', error);
    },
  });

  // ========================================
  // Computed Data
  // ========================================

  const mealItems = useMemo(() =>
    mealItemsQuery.data?.items ?? [],
    [mealItemsQuery.data?.items]
  );

  const mealSections = useMemo(() =>
    mealService.getMealSections(mealItems),
    [mealItems, mealService]
  );

  // ========================================
  // Actions
  // ========================================

  const createMeal = useCallback(
    async (data: MealItemRequest): Promise<MealItem> => {
      return createMutation.mutateAsync(data);
    },
    [createMutation]
  );

  const updateMeal = useCallback(
    async (entryId: string, data: MealItemRequest): Promise<MealItem> => {
      return updateMutation.mutateAsync({ entryId, data });
    },
    [updateMutation]
  );

  const deleteMeal = useCallback(
    async (entryId: string): Promise<void> => {
      return deleteMutation.mutateAsync(entryId);
    },
    [deleteMutation]
  );

  const findFirstMealForNutrition = useCallback(
    (): MealIdentifier | null => {
      return mealService.findFirstMealForNutrition(mealItems);
    },
    [mealService, mealItems]
  );

  const refetch = useCallback(() => {
    mealItemsQuery.refetch();
  }, [mealItemsQuery]);

  const invalidate = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['meal-items', date] });
  }, [queryClient, date]);

  // ========================================
  // Return Model
  // ========================================

  return {
    // Data
    mealItems,
    mealSections,

    // Query state (for backward compatibility)
    mealItemsQuery: {
      isSuccess: mealItemsQuery.isSuccess,
      isLoading: mealItemsQuery.isLoading,
      isError: mealItemsQuery.isError,
      error: mealItemsQuery.error,
      refetch: mealItemsQuery.refetch,
    },

    // State
    isLoading: mealItemsQuery.isLoading,
    isError: mealItemsQuery.isError,
    error: mealItemsQuery.error,

    // CRUD Operations
    createMeal,
    updateMeal,
    deleteMeal,

    // CRUD State
    createMutation: {
      isPending: createMutation.isPending,
      isError: createMutation.isError,
      error: createMutation.error,
    },
    updateMutation: {
      isPending: updateMutation.isPending,
      isError: updateMutation.isError,
      error: updateMutation.error,
    },
    deleteMutation: {
      isPending: deleteMutation.isPending,
      isError: deleteMutation.isError,
      error: deleteMutation.error,
    },
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,

    // Nutrition Analysis
    findFirstMealForNutrition,

    // Data Operations
    refetch,
    invalidate,
  };
}