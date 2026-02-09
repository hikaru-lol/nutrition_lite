/**
 * useMealManager - Layer 4: Feature Logic
 *
 * 責務:
 * - 食事CRUD操作のReact Query統合
 * - 食事関連の非同期データフェッチング協調
 * - UI向けの食事データ統合
 */

'use client';

import { useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useMealService } from '../services/mealService';
import {
  useMealItemsByDate,
  useCreateMealItem,
  useUpdateMealItem,
  useDeleteMealItem
} from './mealOptimisticMutations';
import type { MealItem, MealItemRequest } from '../contract/mealContract';
import type { MealIdentifier, MealSection } from '../services/mealService';

// ========================================
// Types
// ========================================

interface UseMealManagerProps {
  date: string; // YYYY-MM-DD format
}

export interface MealManagerModel {
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

export function useMealManager({
  date,
}: UseMealManagerProps): MealManagerModel {

  // Layer 5 Service注入
  const mealService = useMealService();
  const queryClient = useQueryClient();

  // ========================================
  // Data Fetching
  // ========================================

  // 食事データ取得（既存フックを活用）
  const mealItemsQuery = useMealItemsByDate(date);

  // ========================================
  // CRUD Mutations - 楽観的更新を活用
  // ========================================

  // mealHooks.ts の楽観的更新付き mutation を使用
  const createMutation = useCreateMealItem(date);
  const updateMutation = useUpdateMealItem(date);
  const deleteMutation = useDeleteMealItem(date);

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

  const createMeal = async (data: MealItemRequest): Promise<MealItem> => {
    return createMutation.mutateAsync(data);
  };

  const updateMeal = async (entryId: string, data: MealItemRequest): Promise<MealItem> => {
    return updateMutation.mutateAsync({ entryId, data });
  };

  const deleteMeal = async (entryId: string): Promise<void> => {
    return deleteMutation.mutateAsync(entryId);
  };

  const findFirstMealForNutrition = (): MealIdentifier | null => {
    return mealService.findFirstMealForNutrition(mealItems);
  };

  const refetch = () => {
    mealItemsQuery.refetch();
  };

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['meal-items', 'by-date', date] });
  };

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