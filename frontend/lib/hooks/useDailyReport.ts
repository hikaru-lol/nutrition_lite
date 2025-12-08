// frontend/lib/hooks/useDailyReport.ts
'use client';

import { useEffect, useState } from 'react';
import { fetchMe, type CurrentUser, type UserPlan } from '@/lib/api/auth';
import { fetchProfile, type ProfileResponseApi } from '@/lib/api/profile';
import { fetchMealItems, type MealItemResponse } from '@/lib/api/meals';
import {
  fetchDailyReport,
  generateDailyReport,
  type DailyNutritionReportResponse,
} from '@/lib/api/dailyReport';
import { ApiError } from '@/lib/api/client';

export type Plan = UserPlan;

export type DailyReportVM = {
  date: string;
  summary: string;
  goodPoints: string[];
  improvementPoints: string[];
  tomorrowFocus: string[];
};

export type DailyReportState = {
  plan: Plan;
  hasReport: boolean;
  report?: DailyReportVM;
  isCompleted: boolean;
};

export function useDailyReport(date: string) {
  const [data, setData] = useState<DailyReportState | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<Error | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<Error | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        setIsLoading(true);
        setLoadError(null);

        const [user, profile, meals, report] = await Promise.all([
          fetchMeSafe(),
          fetchProfileSafe(),
          fetchMealItems(date),
          fetchDailyReportSafe(date),
        ]);

        if (cancelled) return;

        if (!user) {
          throw new Error(
            'ユーザー情報の取得に失敗しました。再ログインしてください。'
          );
        }

        const mealsPerDay =
          profile?.meals_per_day ?? inferMealsPerDay(meals) ?? 3;

        const isCompleted = computeIsCompleted(mealsPerDay, meals);

        const vm: DailyReportState = {
          plan: user.plan,
          hasReport: !!report,
          report: report ? mapReportToVM(report) : undefined,
          isCompleted,
        };

        setData(vm);
      } catch (e: any) {
        if (cancelled) return;
        console.error('Failed to load daily report', e);
        setLoadError(e instanceof Error ? e : new Error('Failed to load'));
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

  const generate = async () => {
    if (!data) return;
    setGenerateError(null);

    try {
      setIsGenerating(true);
      await generateDailyReport(date);
      // 生成に成功したら再取得
      setReloadToken((t) => t + 1);
    } catch (e: any) {
      console.error('Failed to generate daily report', e);
      if (e instanceof ApiError) {
        // 400: Daily log not completed / profile missing
        // 409: Already exists (この場合は再取得してもOK)
        if (e.status === 409) {
          setReloadToken((t) => t + 1);
          return;
        }
      }
      setGenerateError(
        e instanceof Error ? e : new Error('Failed to generate')
      );
    } finally {
      setIsGenerating(false);
    }
  };

  // 表に返す error としては「ロードエラー or 生成エラー」をまとめて渡す
  const error = loadError ?? generateError;

  return { data, isLoading, error, generate, isGenerating };
}

// ---- 内部ヘルパー ----

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

async function fetchDailyReportSafe(
  date: string
): Promise<DailyNutritionReportResponse | null> {
  try {
    return await fetchDailyReport(date);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) {
      return null;
    }
    throw e;
  }
}

function inferMealsPerDay(meals: MealItemResponse[]): number | null {
  const mainIndices = meals
    .filter((m) => m.meal_type === 'main' && m.meal_index != null)
    .map((m) => m.meal_index!) as number[];
  if (mainIndices.length === 0) return null;
  return Math.max(...mainIndices);
}

function computeIsCompleted(
  mealsPerDay: number,
  meals: MealItemResponse[]
): boolean {
  const mainIndexSet = new Set<number>();
  for (const m of meals) {
    if (m.meal_type === 'main' && m.meal_index != null) {
      mainIndexSet.add(m.meal_index);
    }
  }
  return mainIndexSet.size >= mealsPerDay;
}

function mapReportToVM(api: DailyNutritionReportResponse): DailyReportVM {
  return {
    date: api.date,
    summary: api.summary,
    goodPoints: api.good_points,
    improvementPoints: api.improvement_points,
    tomorrowFocus: api.tomorrow_focus,
  };
}
