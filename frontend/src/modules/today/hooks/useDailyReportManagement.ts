/**
 * useDailyReportManagement - Layer 4: Feature Logic
 *
 * 日次レポート管理機能
 *
 * 責務:
 * - 日次レポートの取得
 * - 日次レポートの生成
 * - UIに最適化されたインターフェース提供
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getDailyReport, generateDailyReport } from '@/modules/nutrition/api/nutritionClient';
import type { DailyNutritionReport } from '@/modules/nutrition/contract/nutritionContract';

// ========================================
// Types
// ========================================

export interface DailyReportManagementModel {
  report: DailyNutritionReport | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  generateReport: () => Promise<DailyNutritionReport | null>;
  isGenerating: boolean;
  generateError: Error | null;
  refetch: () => void;
}

// ========================================
// Hook Implementation
// ========================================

interface UseDailyReportManagementProps {
  date: string;
  enabled?: boolean;
}

export function useDailyReportManagement({
  date,
  enabled = true,
}: UseDailyReportManagementProps): DailyReportManagementModel {
  const queryClient = useQueryClient();

  // ========================================
  // Query: 日次レポート取得
  // ========================================

  const reportQuery = useQuery({
    queryKey: ['nutrition', 'daily', 'report', date] as const,
    queryFn: () => getDailyReport(date),
    enabled,
    retry: false,
    staleTime: 1000 * 60 * 10, // 10分間キャッシュ
  });

  // ========================================
  // Mutation: 日次レポート生成
  // ========================================

  const generateMutation = useMutation({
    mutationFn: () => generateDailyReport(date),
    onSuccess: () => {
      // レポート生成成功時、キャッシュを無効化して再取得
      queryClient.invalidateQueries({
        queryKey: ['nutrition', 'daily', 'report', date],
      });
    },
  });

  // ========================================
  // Return Model
  // ========================================

  return {
    // データ
    report: reportQuery.data ?? null,

    // Query状態
    isLoading: reportQuery.isLoading,
    isError: reportQuery.isError,
    error: reportQuery.error,

    // Mutationアクション
    generateReport: generateMutation.mutateAsync,

    // Mutation状態
    isGenerating: generateMutation.isPending,
    generateError: generateMutation.error,

    // ユーティリティ
    refetch: reportQuery.refetch,
  };
}
