'use client';

import { useMemo, useState } from 'react';
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
import { fetchProfile } from '@/modules/profile/api/profileClient';

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

interface UseTodayPageModelProps {
  date?: string; // YYYY-MM-DD format
}

export function useTodayPageModel(props: UseTodayPageModelProps = {}) {
  const date = useMemo(() => {
    return props.date || formatLocalDateYYYYMMDD(new Date());
  }, [props.date]);

  // 栄養分析対象の食事選択状態
  const [selectedMealForNutrition, setSelectedMealForNutrition] = useState<{
    meal_type: MealType;
    meal_index: number | null;
  } | null>(null);

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

  // プロフィール情報（食事回数設定のため）
  const profileQuery = useQuery({
    queryKey: ['profile', 'me'] as const,
    queryFn: () => fetchProfile(),
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
  // 実際に存在する最初の食事を使って1日の栄養サマリーを取得
  const firstMealItem = useMemo(() => {
    if (!mealItemsQuery.data?.items?.length) return null;

    // main食事を優先、なければsnackを使用
    const mainMeals = mealItemsQuery.data.items.filter(item => item.meal_type === 'main');
    if (mainMeals.length > 0) {
      return {
        meal_type: mainMeals[0].meal_type,
        meal_index: mainMeals[0].meal_index ?? 1,
      };
    }

    const snackMeals = mealItemsQuery.data.items.filter(item => item.meal_type === 'snack');
    if (snackMeals.length > 0) {
      return {
        meal_type: snackMeals[0].meal_type,
        meal_index: null,
      };
    }

    return null;
  }, [mealItemsQuery.data?.items]);

  const dailySummaryQuery = useQuery({
    queryKey: [
      'nutrition',
      'daily-summary',
      date,
      firstMealItem?.meal_type,
      firstMealItem?.meal_index
    ] as const,
    queryFn: () => {
      if (!firstMealItem) throw new Error('No meals found');
      return recomputeMealAndDaily({
        date,
        meal_type: firstMealItem.meal_type as 'main' | 'snack',
        meal_index: firstMealItem.meal_index,
      });
    },
    enabled: Boolean(
      activeTargetQuery.isSuccess &&
      mealItemsQuery.isSuccess &&
      activeTargetQuery.data !== null &&
      firstMealItem
    ),
    retry: false,
  });

  // エラーは握って dailySummary: null に落とす（Today 自体は生かす）
  const dailySummary: DailyNutritionSummary | null =
    dailySummaryQuery.data?.daily ?? null;

  // ========================================
  // 選択された食事の栄養分析
  // ========================================
  const selectedMealNutritionQuery = useQuery({
    queryKey: [
      'nutrition',
      'selected-meal',
      date,
      selectedMealForNutrition?.meal_type,
      selectedMealForNutrition?.meal_index
    ] as const,
    queryFn: async () => {
      if (!selectedMealForNutrition) {
        throw new Error('No meal selected for nutrition analysis');
      }
      return recomputeMealAndDaily({
        date,
        meal_type: selectedMealForNutrition.meal_type,
        meal_index: selectedMealForNutrition.meal_index,
      });
    },
    enabled: selectedMealForNutrition !== null,
    retry: false,
  });

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
      const actualAmount = actual?.value ?? 0;
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

  // ========================================
  // 日次サマリーデータ（カロリー + PFC）
  // ========================================
  const dailySummaryData = useMemo(() => {
    const target = activeTargetQuery.data;
    if (!target) return null;

    // PFC情報を取得
    const proteinTarget = target.nutrients.find(n => n.code === 'protein');
    const proteinActual = dailySummary?.nutrients.find(n => n.code === 'protein');

    const fatTarget = target.nutrients.find(n => n.code === 'fat');
    const fatActual = dailySummary?.nutrients.find(n => n.code === 'fat');

    const carbohydrateTarget = target.nutrients.find(n => n.code === 'carbohydrate');
    const carbohydrateActual = dailySummary?.nutrients.find(n => n.code === 'carbohydrate');

    // カロリーは PFC から計算（タンパク質・炭水化物: 4kcal/g, 脂質: 9kcal/g）
    const currentCalories =
      ((proteinActual?.value ?? 0) * 4) +
      ((fatActual?.value ?? 0) * 9) +
      ((carbohydrateActual?.value ?? 0) * 4);

    const targetCalories =
      ((proteinTarget?.amount ?? 0) * 4) +
      ((fatTarget?.amount ?? 0) * 9) +
      ((carbohydrateTarget?.amount ?? 0) * 4);

    return {
      currentCalories,
      targetCalories,
      protein: {
        current: proteinActual?.value ?? 0,
        target: proteinTarget?.amount ?? 0,
      },
      fat: {
        current: fatActual?.value ?? 0,
        target: fatTarget?.amount ?? 0,
      },
      carbohydrate: {
        current: carbohydrateActual?.value ?? 0,
        target: carbohydrateTarget?.amount ?? 0,
      },
    };
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

  // 栄養分析対象の食事を選択
  function selectMealForNutrition(meal_type: MealType, meal_index: number | null) {
    setSelectedMealForNutrition({ meal_type, meal_index });
  }

  // 栄養分析をクリア
  function clearSelectedMeal() {
    setSelectedMealForNutrition(null);
  }

  const isLoading = activeTargetQuery.isLoading || mealItemsQuery.isLoading;
  const isError = activeTargetQuery.isError || mealItemsQuery.isError;

  return {
    date,

    // profile
    profileQuery,

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
    dailySummaryData,

    // 栄養素達成度
    nutrientProgress,

    // Phase 7: daily report (E)
    dailyReport,
    dailyReportQuery,
    generateReportMutation,

    // 選択された食事の栄養分析
    selectedMealForNutrition,
    selectedMealNutritionQuery,
    selectMealForNutrition,
    clearSelectedMeal,

    // UI helpers
    mealTypeLabels,

    // ui states
    isLoading,
    isError,
  };
}
