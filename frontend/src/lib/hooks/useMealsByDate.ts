// frontend/lib/hooks/useMealsByDate.ts
'use client';

import { useEffect, useState } from 'react';
import {
  fetchMealItems,
  type MealItemResponse,
  type MealType,
} from '@/lib/api/meals';
import { fetchProfile, type ProfileResponseApi } from '@/lib/api/profile';
import { ApiError } from '@/lib/api/client';

export type MealItemVM = {
  id: string;
  mealType: MealType;
  mealIndex: number | null;
  name: string;
  amountText?: string;
  note?: string | null;
};

export type MealSlot = {
  mealIndex: number;
  items: MealItemVM[];
};

export type MealsView = {
  date: string;
  mealsPerDay: number;
  mainSlots: MealSlot[];
  snacks: MealItemVM[];
};

export function useMealsByDate(date: string) {
  const [data, setData] = useState<MealsView | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const [profile, rawItems] = await Promise.all([
          fetchProfileSafe(),
          fetchMealItems(date),
        ]);

        if (cancelled) return;

        const view = transformMeals(date, rawItems, profile);
        setData(view);
      } catch (e: any) {
        if (cancelled) return;
        console.error('Failed to fetch meals', e);
        setError(e instanceof Error ? e : new Error('Failed to fetch meals'));
        setData(null);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    load();
    return () => {
      cancelled = true;
    };
  }, [date, reloadToken]);

  const refresh = () => setReloadToken((t) => t + 1);

  return { data, isLoading, error, refresh };
}

// ---- 内部ヘルパー ----

async function fetchProfileSafe(): Promise<ProfileResponseApi | null> {
  try {
    const profile = await fetchProfile();
    return profile;
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) {
      return null;
    }
    throw e;
  }
}

function transformMeals(
  date: string,
  items: MealItemResponse[],
  profile: ProfileResponseApi | null
): MealsView {
  const vmItems: MealItemVM[] = items.map((i) => ({
    id: i.id,
    mealType: i.meal_type,
    mealIndex: i.meal_index,
    name: i.name,
    amountText: buildAmountText(i),
    note: i.note,
  }));

  const mainMap = new Map<number, MealItemVM[]>();
  const snacks: MealItemVM[] = [];

  for (const item of vmItems) {
    if (item.mealType === 'main' && item.mealIndex != null) {
      const arr = mainMap.get(item.mealIndex) ?? [];
      arr.push(item);
      mainMap.set(item.mealIndex, arr);
    } else {
      snacks.push(item);
    }
  }

  const mainSlots: MealSlot[] = Array.from(mainMap.entries())
    .sort((a, b) => a[0] - b[0])
    .map(([mealIndex, items]) => ({ mealIndex, items }));

  const mealsPerDay =
    profile?.meals_per_day ??
    (mainSlots.length > 0 ? Math.max(...mainSlots.map((s) => s.mealIndex)) : 3);

  return { date, mealsPerDay, mainSlots, snacks };
}

function buildAmountText(i: MealItemResponse): string | undefined {
  if (i.amount_value != null && i.amount_unit) {
    return `${i.amount_value}${i.amount_unit}`;
  }
  if (i.serving_count != null) {
    return `${i.serving_count} serving`;
  }
  return undefined;
}
