// src/modules/meal/model/hooks.ts
'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { mealApi } from '../api/client';
import type {
  MealItemListResponse,
  MealItemRequest,
  MealItemResponse,
} from '../api/types';
import { mealKeys } from './keys';

function upsertItem(
  list: MealItemListResponse | undefined,
  item: MealItemResponse
): MealItemListResponse | undefined {
  if (!list) return list;
  const exists = list.items.some((x) => x.id === item.id);
  const items = exists
    ? list.items.map((x) => (x.id === item.id ? item : x))
    : [item, ...list.items];
  return { items };
}

function removeItem(
  list: MealItemListResponse | undefined,
  entryId: string
): MealItemListResponse | undefined {
  if (!list) return list;
  return { items: list.items.filter((x) => x.id !== entryId) };
}

/** 指定日付の FoodEntry 一覧 */
export function useMealItems(date: string, opts?: { enabled?: boolean }) {
  return useQuery({
    queryKey: mealKeys.itemsByDate(date),
    queryFn: () => mealApi.listByDate(date),
    enabled: opts?.enabled ?? Boolean(date),
  });
}

/** FoodEntry 作成（成功時：その日の一覧キャッシュに即反映） */
export function useCreateMealItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: MealItemRequest) => mealApi.create(body),
    onSuccess: (created) => {
      qc.setQueryData<MealItemListResponse | undefined>(
        mealKeys.itemsByDate(created.date),
        (prev) => upsertItem(prev, created)
      );

      // 安全寄りに再取得して整合させたい場合は invalidate でもOK
      // qc.invalidateQueries({ queryKey: mealKeys.itemsByDate(created.date) });

      // （後で modules/nutrition を作ったら）ここで nutrition系キーを invalidate するのが定石
    },
  });
}

/** FoodEntry 更新（成功時：その日の一覧キャッシュに即反映） */
export function useUpdateMealItem(entryId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: MealItemRequest) => mealApi.update(entryId, body),
    onSuccess: (updated) => {
      qc.setQueryData<MealItemListResponse | undefined>(
        mealKeys.itemsByDate(updated.date),
        (prev) => upsertItem(prev, updated)
      );
      // qc.invalidateQueries({ queryKey: mealKeys.itemsByDate(updated.date) });
    },
  });
}

/**
 * FoodEntry 削除
 * 204 で返るので date は呼び出し側から渡す（削除後にどのキャッシュを触るか確定させるため）
 */
export function useDeleteMealItem(date: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (entryId: string) => mealApi.delete(entryId),
    onSuccess: (_void, entryId) => {
      qc.setQueryData<MealItemListResponse | undefined>(
        mealKeys.itemsByDate(date),
        (prev) => removeItem(prev, entryId)
      );
      // qc.invalidateQueries({ queryKey: mealKeys.itemsByDate(date) });
    },
  });
}
