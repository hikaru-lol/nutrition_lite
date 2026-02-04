/**
 * useTodayReports - レポート管理専用フック
 *
 * 責務:
 * - 日次レポートの取得・生成
 * - レポート生成条件の検証
 * - 強化版レポートの管理
 */

'use client';

import { useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import { todayQueryKeys } from '../lib/queryKeys';
import type {
  TodayReportsModel,
  ValidationState,
  formatLocalDateYYYYMMDD,
} from '../types/todayTypes';
import {
  getDailyReport,
  generateDailyReport,
} from '@/modules/nutrition/api/nutritionClient';
import type {
  DailyNutritionReport,
} from '@/modules/nutrition/contract/nutritionContract';

// ========================================
// Props Interface
// ========================================

interface UseTodayReportsProps {
  date?: string; // YYYY-MM-DD format
  mealItemsCount?: number; // 食事アイテム数（検証用）
  mealsPerDay?: number;    // 1日の食事回数（検証用）
}

// ========================================
// Main Hook
// ========================================

export function useTodayReports(props: UseTodayReportsProps = {}): TodayReportsModel {
  const queryClient = useQueryClient();

  // 日付の正規化
  const date = useMemo(() => {
    return props.date || formatLocalDateYYYYMMDD(new Date());
  }, [props.date]);

  // ========================================
  // Data Fetching
  // ========================================

  // 日次レポート取得
  const dailyReportQuery = useQuery({
    queryKey: todayQueryKeys.dailyReport(date),
    queryFn: () => getDailyReport(date),
    retry: false,
  });

  // ========================================
  // Mutations
  // ========================================

  // 日次レポート生成
  const generateReportMutation = useMutation({
    mutationFn: ({ date }: { date: string }) => generateDailyReport(date),
    onMutate: () => {
      toast.loading('レポートを生成しています...', {
        id: 'generate-report',
      });
    },
    onSuccess: (data) => {
      toast.dismiss('generate-report');
      toast.success('レポートが生成されました');

      // キャッシュを更新
      queryClient.setQueryData(todayQueryKeys.dailyReport(date), data);
    },
    onError: (error) => {
      toast.dismiss('generate-report');
      console.error('レポート生成エラー:', error);
      toast.error('レポートの生成に失敗しました');
    },
  });

  // ========================================
  // Validation Logic
  // ========================================

  // 食事完了度の検証
  const validationState: ValidationState = useMemo(() => {
    const mealItemsCount = props.mealItemsCount ?? 0;
    const mealsPerDay = props.mealsPerDay ?? 3;

    // 食事完了度の計算
    const completionPercentage = mealsPerDay > 0 ? (mealItemsCount / mealsPerDay) * 100 : 0;
    const isMealCompletionValid = completionPercentage >= 50; // 50%以上で有効

    // 不足している食事回数
    const missingMealsCount = Math.max(0, mealsPerDay - mealItemsCount);

    // データ十分性の判定
    const hasEnoughData = mealItemsCount >= Math.floor(mealsPerDay / 2);

    // 完了ステータス
    const mealCompletionStatus = {
      percentage: Math.round(completionPercentage),
      completed: mealItemsCount,
      total: mealsPerDay,
      status: isMealCompletionValid ? 'sufficient' : 'insufficient',
    };

    return {
      isMealCompletionValid,
      mealCompletionStatus,
      missingMealsCount,
      hasEnoughData,
    };
  }, [props.mealItemsCount, props.mealsPerDay]);

  // ========================================
  // Enhanced Report Logic
  // ========================================

  // 強化版レポート（複数レポートを統合）
  const enhancedReport = useMemo(() => {
    const dailyReport = dailyReportQuery.data;
    if (!dailyReport) return null;

    // ここで追加の分析ロジックを実装
    // 例: トレンド分析、栄養バランススコア、改善提案等
    return {
      basic: dailyReport,
      trends: {
        // 週次トレンド等
        weeklyProgress: null,
        monthlyProgress: null,
      },
      insights: {
        // AI分析結果
        nutritionScore: calculateNutritionScore(dailyReport),
        improvements: generateImprovementSuggestions(dailyReport),
      },
      metadata: {
        generatedAt: new Date().toISOString(),
        version: '1.0',
      },
    };
  }, [dailyReportQuery.data]);

  // ========================================
  // Actions Implementation
  // ========================================

  const generateReport = async (targetDate: string): Promise<void> => {
    // 生成前の検証
    if (!validationState.hasEnoughData) {
      toast.error('レポート生成には十分な食事データが必要です');
      return;
    }

    return generateReportMutation.mutateAsync({ date: targetDate });
  };

  const fetchReport = (targetDate: string): void => {
    // 手動でレポートを再取得
    queryClient.invalidateQueries({
      queryKey: todayQueryKeys.dailyReport(targetDate),
    });
  };

  // ========================================
  // Return Value
  // ========================================

  return {
    // State
    dailyReport: dailyReportQuery.data ?? null,
    enhancedReport,
    isLoading: dailyReportQuery.isLoading,
    isError: dailyReportQuery.isError,
    isGenerating: generateReportMutation.isPending,
    generateError: generateReportMutation.error,
    queryError: dailyReportQuery.error,

    // Actions
    generateReport,
    fetchReport,

    // Validation
    validationState,
  };
}

// ========================================
// ヘルパー関数
// ========================================

/**
 * 栄養スコアを計算
 */
function calculateNutritionScore(report: DailyNutritionReport): number {
  if (!report.analysis || !report.daily?.nutrients) {
    return 0;
  }

  // 基本的なスコア計算ロジック
  const nutrients = report.daily.nutrients;
  const proteinScore = Math.min(100, (nutrients.find(n => n.code === 'protein')?.value ?? 0) / 50 * 100);
  const vitaminScore = Math.min(100, (nutrients.find(n => n.code === 'vitamin_d')?.value ?? 0) / 10 * 100);

  return Math.round((proteinScore + vitaminScore) / 2);
}

/**
 * 改善提案を生成
 */
function generateImprovementSuggestions(report: DailyNutritionReport): string[] {
  const suggestions: string[] = [];

  if (!report.daily?.nutrients) {
    return ['データが不足しています'];
  }

  const nutrients = report.daily.nutrients;

  // タンパク質チェック
  const protein = nutrients.find(n => n.code === 'protein')?.value ?? 0;
  if (protein < 50) {
    suggestions.push('タンパク質を増やしましょう（魚、肉、豆類を追加）');
  }

  // ビタミンDチェック
  const vitaminD = nutrients.find(n => n.code === 'vitamin_d')?.value ?? 0;
  if (vitaminD < 5) {
    suggestions.push('ビタミンDを増やしましょう（魚、きのこ類を追加）');
  }

  // 食物繊維チェック
  const fiber = nutrients.find(n => n.code === 'fiber')?.value ?? 0;
  if (fiber < 20) {
    suggestions.push('食物繊維を増やしましょう（野菜、穀物を追加）');
  }

  return suggestions.length > 0 ? suggestions : ['バランスの良い食事を継続しましょう'];
}

// ========================================
// 軽量版Hook（検証のみ）
// ========================================

/**
 * レポート生成条件の検証のみを行う軽量フック
 */
export function useReportValidation(props: Omit<UseTodayReportsProps, 'date'>) {
  const { validationState } = useTodayReports(props);
  return validationState;
}