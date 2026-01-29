'use client';

import { useMemo } from 'react';
import { z } from 'zod';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import {
  fetchActiveTarget,
  listTargets,
  deleteTarget,
  activateTarget,
} from '@/modules/target/api/targetClient';
import {
  MealItemRequestSchema,
  type MealItemRequest,
  type MealType,
} from '@/modules/meal/contract/mealContract';
import {
  useMealItemsByDate,
  useCreateMealItem,
  useDeleteMealItem,
} from '@/modules/meal/model/mealHooks';
import {
  recomputeMealAndDaily,
  getDailyReport,
  generateDailyReport,
} from '@/modules/nutrition/api/nutritionClient';
import type {
  DailyNutritionSummary,
  DailyNutritionReport,
} from '@/modules/nutrition/contract/nutritionContract';
import type { NutrientCode } from '@/modules/target/contract/targetContract';

function formatLocalDateYYYYMMDD(d: Date): string {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

const MealItemFormSchema = MealItemRequestSchema.extend({
  // UIフォーム的に: meal_index は main のとき必須、snack のとき null
  meal_index: z.number().int().min(1).nullable().optional(),
});

export type TodayMealItemFormValues = z.infer<typeof MealItemFormSchema>;

// 栄養素コード → 日本語ラベル
const nutrientLabels: Record<NutrientCode, string> = {
  carbohydrate: '炭水化物',
  fat: '脂質',
  protein: 'たんぱく質',
  water: '水分',
  fiber: '食物繊維',
  sodium: 'ナトリウム',
  iron: '鉄',
  calcium: 'カルシウム',
  vitamin_d: 'ビタミンD',
  potassium: 'カリウム',
};

// 達成度の型
export type NutrientProgress = {
  code: NutrientCode;
  label: string;
  target: number;
  actual: number;
  unit: string;
  percentage: number;
};

export function useTodayPageModel() {
  const date = useMemo(() => formatLocalDateYYYYMMDD(new Date()), []);

  // Target（active）
  // → Query を Today で持ってもOKだが、まずは最小で「取得できる/できない」だけ欲しいので
  // useQuery を書いても良い。ここでは “今後の拡張” 前提で useMutation+manual fetch にせず、
  // ちゃんと useQuery を切っておくのがよい。
  // ※簡潔さのため、下の UI で useQuery を持たせたくないので、ここで useQuery を持つ。

  // TanStack Query を使うために import を増やしたいが、
  // 依存方向は Model → API なので問題なし。
  const activeTargetQuery = useQuery({
    queryKey: ['targets', 'active'] as const,
    queryFn: () => fetchActiveTarget(),
    retry: false,
  });

  // ターゲット一覧
  const targetsListQuery = useQuery({
    queryKey: ['targets', 'list'] as const,
    queryFn: () => listTargets(),
    retry: false,
  });

  // Meal（今日）
  const mealItemsQuery = useMealItemsByDate(date);

  const createMutation = useCreateMealItem(date);
  const deleteMutation = useDeleteMealItem(date);

  const queryClient = useQueryClient();

  // ========================================
  // Phase 6: Daily Nutrition Summary (C)
  // ========================================
  // main meal (index=1) の栄養サマリーを取得
  // enabled: target と meal が取得できている場合のみ
  const dailySummaryQuery = useQuery({
    queryKey: ['nutrition', 'meal', date, 'main', 1] as const,
    queryFn: () =>
      recomputeMealAndDaily({ date, meal_type: 'main', meal_index: 1 }),
    enabled:
      activeTargetQuery.isSuccess &&
      mealItemsQuery.isSuccess &&
      activeTargetQuery.data !== null,
    retry: false,
  });

  // エラーは握って dailySummary: null に落とす（Today 自体は生かす）
  const dailySummary: DailyNutritionSummary | null =
    dailySummaryQuery.data?.daily ?? null;

  // ========================================
  // Phase 7: Daily Report (E)
  // ========================================
  const dailyReportQuery = useQuery({
    queryKey: ['nutrition', 'daily', 'report', date] as const,
    queryFn: () => getDailyReport(date),
    enabled:
      activeTargetQuery.isSuccess &&
      mealItemsQuery.isSuccess &&
      activeTargetQuery.data !== null,
    retry: false,
  });

  const dailyReport: DailyNutritionReport | null =
    dailyReportQuery.data ?? null;

  // ========================================
  // 栄養素達成度の計算
  // ========================================
  const nutrientProgress: NutrientProgress[] = useMemo(() => {
    const target = activeTargetQuery.data;
    if (!target) return [];

    // dailySummary がなくても target があれば目標値を表示（実績は 0）
    return target.nutrients.map((t) => {
      const actual = dailySummary?.nutrients.find((n) => n.code === t.code);
      const actualAmount = actual?.amount ?? 0;
      const percentage = t.amount > 0 ? (actualAmount / t.amount) * 100 : 0;

      return {
        code: t.code,
        label: nutrientLabels[t.code],
        target: t.amount,
        actual: actualAmount,
        unit: t.unit,
        percentage,
      };
    });
  }, [activeTargetQuery.data, dailySummary]);

  const generateReportMutation = useMutation({
    mutationFn: () => generateDailyReport(date),
    onSuccess: async () => {
      // 成功/409 → refetch
      await queryClient.invalidateQueries({
        queryKey: ['nutrition', 'daily', 'report', date],
      });
    },
  });

  // ========================================
  // ターゲット削除・アクティブ化
  // ========================================
  const deleteTargetMutation = useMutation({
    mutationFn: (targetId: string) => deleteTarget(targetId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['targets'] });
    },
  });

  const activateTargetMutation = useMutation({
    mutationFn: (targetId: string) => activateTarget(targetId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['targets'] });
    },
  });

  const mealTypeLabels: Record<MealType, string> = {
    main: 'メイン',
    snack: '間食',
  };

  // UI入力 → API入力（contract）へ整形
  async function addMealItem(v: TodayMealItemFormValues) {
    const safe = MealItemFormSchema.parse(v);

    const req: MealItemRequest = {
      ...safe,
      // snack の場合は meal_index を null に寄せる
      meal_index: safe.meal_type === 'snack' ? null : safe.meal_index ?? 1,
    };

    await createMutation.mutateAsync(req);
  }

  async function removeMealItem(entryId: string) {
    await deleteMutation.mutateAsync(entryId);
  }

  const isLoading = activeTargetQuery.isLoading || mealItemsQuery.isLoading;
  const isError = activeTargetQuery.isError || mealItemsQuery.isError;

  return {
    date,

    // target
    activeTargetQuery,
    targetsListQuery,
    deleteTargetMutation,
    activateTargetMutation,

    // meals
    mealItemsQuery,
    addMealItem,
    removeMealItem,
    createMutation,
    deleteMutation,

    // Phase 6: daily summary (C)
    dailySummary,
    dailySummaryQuery,

    // 栄養素達成度
    nutrientProgress,

    // Phase 7: daily report (E)
    dailyReport,
    dailyReportQuery,
    generateReportMutation,

    // UI helpers
    mealTypeLabels,

    // ui states
    isLoading,
    isError,
  };
}
