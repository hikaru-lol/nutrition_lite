/**
 * useTodayMeals - 食事管理専用フック
 *
 * 責務:
 * - 食事アイテムの CRUD 操作
 * - 食事データの取得とキャッシュ管理
 * - ローディング・エラー状態の管理
 */

'use client';

import { useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import { todayQueryKeys } from '../lib/queryKeys';
import type {
  TodayMealsModel,
  TodayMealItemFormValues,
  formatLocalDateYYYYMMDD,
} from '../types/todayTypes';
import {
  useMealItemsByDate,
  useCreateMealItem,
  useDeleteMealItem,
} from '@/modules/meal/model/mealHooks';
import { useUpdateMealItem } from '@/modules/meal/model/mealHooks';

// ========================================
// Props Interface
// ========================================

interface UseTodayMealsProps {
  date?: string; // YYYY-MM-DD format
}

// ========================================
// Main Hook
// ========================================

export function useTodayMeals(props: UseTodayMealsProps = {}): TodayMealsModel {
  const queryClient = useQueryClient();

  // 日付の正規化
  const date = useMemo(() => {
    return props.date || formatLocalDateYYYYMMDD(new Date());
  }, [props.date]);

  // ========================================
  // Data Fetching
  // ========================================

  // 食事アイテム取得（既存のフックを再利用）
  const mealItemsQuery = useMealItemsByDate(date);

  // ========================================
  // Mutations
  // ========================================

  // 食事アイテム作成（既存のフックを再利用）
  const createMutation = useCreateMealItem(date);

  // 食事アイテム削除（既存のフックを再利用）
  const deleteMutation = useDeleteMealItem(date);

  // 食事アイテム更新（既存のフックを再利用）
  const updateMutation = useUpdateMealItem(date);

  // ========================================
  // Actions Implementation
  // ========================================

  const addMealItem = async (values: TodayMealItemFormValues): Promise<void> => {
    try {
      await createMutation.mutateAsync(values);
      toast.success('食事を追加しました');
    } catch (error) {
      console.error('Failed to add meal item:', error);
      toast.error('食事の追加に失敗しました');
      throw error;
    }
  };

  const removeMealItem = async (id: string): Promise<void> => {
    try {
      await deleteMutation.mutateAsync(id);
      toast.success('食事を削除しました');
    } catch (error) {
      console.error('Failed to delete meal item:', error);
      toast.error('食事の削除に失敗しました');
      throw error;
    }
  };

  const updateMealItem = async (entryId: string, values: any): Promise<void> => {
    try {
      await updateMutation.mutateAsync({ entryId, data: values });
      toast.success('食事を更新しました');
    } catch (error) {
      console.error('Failed to update meal item:', error);
      toast.error('食事の更新に失敗しました');
      throw error;
    }
  };

  // ========================================
  // 削除状態管理（複数アイテム対応）
  // ========================================

  const isDeletingMap = useMemo(() => {
    // 現在は単一削除のみなので、削除中のアイテムIDをマップ化
    const map: Record<string, boolean> = {};
    if (deleteMutation.isPending && deleteMutation.variables) {
      map[deleteMutation.variables] = true;
    }
    return map;
  }, [deleteMutation.isPending, deleteMutation.variables]);

  // ========================================
  // Return Value
  // ========================================

  return {
    // State
    items: mealItemsQuery.data?.items ?? [],
    isLoading: mealItemsQuery.isLoading,
    isError: mealItemsQuery.isError,
    isDeletingMap,

    // Actions
    add: addMealItem,
    remove: removeMealItem,
    update: updateMealItem,
  };
}

// ========================================
// 軽量版Hook（読み取り専用）
// ========================================

/**
 * 食事データの読み取り専用フック
 * Actionsが不要な場合に使用してパフォーマンスを向上
 */
export function useTodayMealsReadOnly(props: UseTodayMealsProps = {}) {
  const date = useMemo(() => {
    return props.date || formatLocalDateYYYYMMDD(new Date());
  }, [props.date]);

  const mealItemsQuery = useMealItemsByDate(date);

  return {
    items: mealItemsQuery.data?.items ?? [],
    isLoading: mealItemsQuery.isLoading,
    isError: mealItemsQuery.isError,
    count: mealItemsQuery.data?.items.length ?? 0,
  };
}