/**
 * チュートリアル機能のState Management層
 * TanStack Queryベースのデータ管理
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchTutorialStatus, completeTutorial } from '../api/tutorialClient';
import type { TutorialId, TutorialState } from '../contract/tutorialContract';

/**
 * クエリキー定義
 */
export const tutorialQueryKeys = {
  all: ['tutorial'] as const,
  status: () => [...tutorialQueryKeys.all, 'status'] as const,
};

/**
 * チュートリアル状況取得Query
 */
export function useTutorialStatusQuery() {
  return useQuery({
    queryKey: tutorialQueryKeys.status(),
    queryFn: fetchTutorialStatus,
    staleTime: 5 * 60 * 1000, // 5分間キャッシュ
    gcTime: 10 * 60 * 1000, // 10分間メモリ保持
  });
}

/**
 * チュートリアル完了Mutation
 */
export function useCompleteTutorialMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (tutorialId: TutorialId) => completeTutorial(tutorialId),
    onSuccess: (data) => {
      // 状況クエリを無効化して最新データを取得
      queryClient.invalidateQueries({ queryKey: tutorialQueryKeys.status() });

      // 楽観的アップデート: キャッシュに新しい完了記録を追加
      queryClient.setQueryData(tutorialQueryKeys.status(), (oldData: any) => {
        if (!oldData) return oldData;
        const newCompleted = [...(oldData.completed || []), data.tutorial_id];
        return {
          ...oldData,
          completed: Array.from(new Set(newCompleted)), // 重複除去
        };
      });
    },
    onError: (error) => {
      console.error('チュートリアル完了エラー:', error);
    },
  });
}

/**
 * チュートリアル状態管理フック (メイン)
 */
export function useTutorialModel() {
  const statusQuery = useTutorialStatusQuery();
  const completeMutation = useCompleteTutorialMutation();

  // 現在の状態を算出
  const tutorialState: TutorialState = {
    completedTutorials: (statusQuery.data?.completed || []) as TutorialId[],
    currentTutorial: null, // 実行中チュートリアルはUI側で管理
    isRunning: false, // 実行中フラグはUI側で管理
    isLoading: statusQuery.isLoading,
  };

  /**
   * 指定したチュートリアルが完了済みかチェック
   */
  const isTutorialCompleted = (tutorialId: TutorialId): boolean => {
    return tutorialState.completedTutorials.includes(tutorialId);
  };

  /**
   * チュートリアルを完了済みとしてマーク
   */
  const markAsCompleted = (tutorialId: TutorialId) => {
    if (!isTutorialCompleted(tutorialId)) {
      completeMutation.mutate(tutorialId);
    }
  };

  /**
   * 完了済みチュートリアル数
   */
  const completedCount = tutorialState.completedTutorials.length;

  /**
   * 全チュートリアル数 (契約層で定義済み)
   */
  const totalCount = 5; // onboarding_profile, onboarding_target, feature_today, feature_calendar, feature_nutrition

  /**
   * 進捗率 (%)
   */
  const progressPercentage = Math.round((completedCount / totalCount) * 100);

  return {
    // 状態
    tutorialState,
    isLoading: statusQuery.isLoading,
    error: statusQuery.error || completeMutation.error,

    // データ
    completedTutorials: tutorialState.completedTutorials,
    completedCount,
    totalCount,
    progressPercentage,

    // アクション
    isTutorialCompleted,
    markAsCompleted,

    // ローレベルアクセス
    statusQuery,
    completeMutation,

    // リフレッシュ
    refetch: statusQuery.refetch,
  };
}