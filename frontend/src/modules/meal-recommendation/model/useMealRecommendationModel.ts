'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMemo } from 'react';
import { qk } from '@/shared/lib/query/keys';
import { mealRecommendationApi } from '../api/mealRecommendationClient';
import type {
  MealRecommendationCardState,
  GenerateMealRecommendationRequest,
} from '../contract/mealRecommendationContract';
import {
  MealRecommendationCooldownError,
  MealRecommendationDailyLimitError,
} from '../contract/mealRecommendationContract';
import { useFeatureLimitCheck } from '@/modules/billing';

// =============================================================================
// 型定義
// =============================================================================

export interface UseMealRecommendationModelOptions {
  date?: string;  // YYYY-MM-DD
  enabled?: boolean;
}

// =============================================================================
// 状態管理Hook
// =============================================================================

export function useMealRecommendationModel(options: UseMealRecommendationModelOptions = {}) {
  const queryClient = useQueryClient();
  const { date, enabled = true } = options;
  const { checkMealRecommendationLimit } = useFeatureLimitCheck();

  // クエリ：特定日の食事提案取得
  const todayQuery = useQuery({
    queryKey: qk.mealRecommendation.byDate(date || 'today'),
    queryFn: async () => {
      if (!date) {
        // 日付が指定されていない場合はリストから最新を取得
        const listResponse = await mealRecommendationApi.list({ limit: 1 });
        return listResponse.recommendations[0] || null;
      }

      try {
        const response = await mealRecommendationApi.getByDate(date);
        return response.recommendation;
      } catch (error) {
        // 404の場合はnullを返す（未生成状態）
        const status = (error as { status?: number })?.status;
        const message = (error as { message?: string })?.message || '';
        if (status === 404 || message.includes('404') || message.includes('not found') || message.includes('Recommendation not found')) {
          return null;
        }
        throw error;
      }
    },
    enabled,
    staleTime: 5 * 60 * 1000, // 5分間キャッシュ
  });

  // クエリ：食事提案リスト取得
  const listQuery = useQuery({
    queryKey: qk.mealRecommendation.list(10),
    queryFn: () => mealRecommendationApi.list({ limit: 10 }),
    enabled: false, // 手動でトリガー
    staleTime: 5 * 60 * 1000, // 5分間キャッシュ
  });

  // ミューテーション：食事提案生成
  const generateMutation = useMutation({
    mutationFn: (data: GenerateMealRecommendationRequest) =>
      mealRecommendationApi.generate(data),
    onSuccess: () => {
      // 生成成功時にクエリを無効化して最新データを取得
      queryClient.invalidateQueries({
        queryKey: qk.mealRecommendation.byDate(date || 'today')
      });
      queryClient.invalidateQueries({
        queryKey: qk.mealRecommendation.list()
      });
    },
  });

  // 派生状態の計算
  const cardState = useMemo((): MealRecommendationCardState => {
    const isLoading = todayQuery.isLoading;
    const isGenerating = generateMutation.isPending;
    const error = todayQuery.error || generateMutation.error;
    const recommendation = todayQuery.data;

    // ローディング状態
    if (isLoading || isGenerating) {
      return {
        status: 'loading',
        canGenerate: false,
      };
    }

    // エラー状態
    if (error) {
      let canGenerate = true;
      let nextGenerationTime: Date | undefined;
      let remainingGenerations: number | undefined;

      if (error instanceof MealRecommendationCooldownError) {
        canGenerate = false;
        nextGenerationTime = new Date(new Date().getTime() + error.minutes * 60 * 1000);
      } else if (error instanceof MealRecommendationDailyLimitError) {
        canGenerate = false;
        remainingGenerations = error.limit - error.currentCount;
      }

      return {
        status: error instanceof MealRecommendationCooldownError ||
                error instanceof MealRecommendationDailyLimitError ? 'rate-limited' : 'error',
        error,
        canGenerate,
        nextGenerationTime,
        remainingGenerations,
      };
    }

    // データが存在する場合
    if (recommendation) {
      return {
        status: 'available',
        recommendation,
        canGenerate: true,
      };
    }

    // 未生成状態
    return {
      status: 'empty',
      canGenerate: true,
    };
  }, [todayQuery.isLoading, todayQuery.error, todayQuery.data, generateMutation.isPending, generateMutation.error]);

  // アクション関数
  const actions = useMemo(() => ({
    generate: (data: GenerateMealRecommendationRequest = {}) => {
      generateMutation.mutate(date ? { ...data, date } : data);
    },

    refresh: () => {
      queryClient.invalidateQueries({
        queryKey: qk.mealRecommendation.byDate(date || 'today')
      });
    },

    loadHistory: () => {
      listQuery.refetch();
    },
  }), [generateMutation, queryClient, date, listQuery]);

  // プラン制限チェック（今日の生成回数を仮定、実際の回数は適宜調整）
  const currentCount = useMemo(() => {
    // TODO: 実際の今日の生成回数を取得するロジックを実装
    // 現在は仮の値として0を使用
    return listQuery.data?.recommendations?.filter(r =>
      new Date(r.created_at).toDateString() === new Date().toDateString()
    ).length || 0;
  }, [listQuery.data]);

  const planLimit = checkMealRecommendationLimit(currentCount);

  return {
    // 状態
    cardState,

    // データ
    recommendation: todayQuery.data,
    recommendations: listQuery.data?.recommendations,

    // ローディング状態
    isLoading: todayQuery.isLoading,
    isGenerating: generateMutation.isPending,
    isLoadingHistory: listQuery.isLoading,

    // エラー
    error: todayQuery.error || generateMutation.error,

    // プラン制限情報
    planLimit,
    currentCount,

    // アクション
    ...actions,
  };
}