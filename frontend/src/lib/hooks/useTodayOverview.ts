// frontend/lib/hooks/useTodayOverview.ts
'use client';

import { useEffect, useState } from 'react';
import { fetchMe, type CurrentUser, type UserPlan } from '@/lib/api/auth';
import { fetchMealItems, type MealItemResponse } from '@/lib/api/meals';
import { fetchDailyReport } from '@/lib/api/dailyReport';
import { fetchProfile, type ProfileResponseApi } from '@/lib/api/profile';
import { ApiError } from '@/lib/api/client';
// ★ Recommendation の API を後で定義（現時点では未接続でもOK）
// import { fetchLatestRecommendation } from "@/lib/api/recommendation";

export type Plan = UserPlan;

export type TodayProgress = {
  date: string;
  mealsPerDay: number;
  filledCount: number;
  isCompleted: boolean;
};

export type TodayMealsSummary = {
  date: string;
  mainMeals: { mealIndex: number; itemCount: number }[];
  snackCount: number;
};

export type TodayReportPreview = {
  date: string;
  hasReport: boolean;
  summary?: string;
};

export type TodayRecommendationPreview = {
  date: string;
  hasRecommendation: boolean;
  snippet?: string;
};

export type TodayOverview = {
  userName: string;
  plan: Plan;
  trialEndsAt: string | null;
  progress: TodayProgress;
  mealsSummary: TodayMealsSummary;
  reportPreview: TodayReportPreview;
  recommendationPreview: TodayRecommendationPreview;
};

export function useTodayOverview(targetDate?: string) {
  const [data, setData] = useState<TodayOverview | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const date = targetDate ?? new Date().toISOString().slice(0, 10);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // まずは user, profile, meals だけまとめて取得
        const [user, profile, mealItems] = await Promise.all([
          fetchMeSafe(),
          fetchProfileSafe(),
          fetchMealItems(date),
        ]);

        if (cancelled) return;
        if (!user) {
          throw new Error(
            'ユーザー情報の取得に失敗しました。再ログインしてください。'
          );
        }

        // meals_per_day の決定
        const mealsPerDay =
          profile?.meals_per_day ?? inferMealsPerDay(mealItems) ?? 3;

        const progress = buildTodayProgress(date, mealsPerDay, mealItems);
        const mealsSummary = buildTodayMealsSummary(date, mealItems);

        // レポート preview
        let reportPreview: TodayReportPreview = {
          date,
          hasReport: false,
          summary: undefined,
        };

        if (user.plan !== 'free') {
          const report = await fetchDailyReportSafe(date);
          if (!cancelled && report) {
            reportPreview = {
              date,
              hasReport: true,
              summary: report.summary,
            };
          }
        }

        // 提案 preview（現時点ではプレースホルダ）
        const recommendationPreview: TodayRecommendationPreview = {
          date,
          hasRecommendation: false,
          snippet: undefined,
        };
        // 将来的に:
        // if (user.plan !== "free") {
        //   const reco = await fetchLatestRecommendationSafe();
        //   ...
        // }

        const overview: TodayOverview = {
          userName: user.name ?? user.email,
          plan: user.plan,
          trialEndsAt: user.trialEndsAt,
          progress,
          mealsSummary,
          reportPreview,
          recommendationPreview,
        };

        if (!cancelled) setData(overview);
      } catch (e: any) {
        if (cancelled) return;
        console.error('Failed to load Today overview', e);
        setError(e instanceof Error ? e : new Error('Unknown error'));
        setData(null);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    load();
    return () => {
      cancelled = true;
    };
  }, [date]);

  return { data, isLoading, error };
}

// ---------- helpers ----------

async function fetchMeSafe(): Promise<CurrentUser | null> {
  try {
    return await fetchMe();
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) {
      return null;
    }
    throw e;
  }
}

async function fetchProfileSafe(): Promise<ProfileResponseApi | null> {
  try {
    return await fetchProfile();
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) {
      return null;
    }
    throw e;
  }
}

async function fetchDailyReportSafe(date: string) {
  try {
    return await fetchDailyReport(date);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) {
      return null;
    }
    // FREE / プラン制限で 403 を返すようにした場合にもここで握る
    if (e instanceof ApiError && e.status === 403) {
      return null;
    }
    throw e;
  }
}

function buildTodayProgress(
  date: string,
  mealsPerDay: number,
  mealItems: MealItemResponse[]
): TodayProgress {
  const mainItems = mealItems.filter(
    (m) => m.meal_type === 'main' && m.meal_index != null
  );
  const mainIndexSet = new Set<number>();
  for (const item of mainItems) {
    if (item.meal_index != null) mainIndexSet.add(item.meal_index);
  }
  const filledCount = mainIndexSet.size;
  const isCompleted = filledCount >= mealsPerDay;

  return { date, mealsPerDay, filledCount, isCompleted };
}

function buildTodayMealsSummary(
  date: string,
  mealItems: MealItemResponse[]
): TodayMealsSummary {
  const mainMap = new Map<number, number>();
  let snackCount = 0;

  for (const item of mealItems) {
    if (item.meal_type === 'main' && item.meal_index != null) {
      const count = mainMap.get(item.meal_index) ?? 0;
      mainMap.set(item.meal_index, count + 1);
    } else if (item.meal_type === 'snack') {
      snackCount += 1;
    }
  }

  const mainMeals = Array.from(mainMap.entries())
    .sort((a, b) => a[0] - b[0])
    .map(([mealIndex, itemCount]) => ({ mealIndex, itemCount }));

  return { date, mainMeals, snackCount };
}

function inferMealsPerDay(mealItems: MealItemResponse[]): number | null {
  const mainIndices = mealItems
    .filter((m) => m.meal_type === 'main' && m.meal_index != null)
    .map((m) => m.meal_index!) as number[];
  if (mainIndices.length === 0) return null;
  return Math.max(...mainIndices);
}
