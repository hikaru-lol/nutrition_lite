/**
 * useTargetManager - Layer 4: Feature Logic
 *
 * ターゲット管理機能
 *
 * 責務:
 * - ターゲット一覧の取得
 * - ターゲットの削除
 * - ターゲットのアクティブ化
 * - UIに最適化されたインターフェース提供
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTargetService } from '../services/targetService';
import type { Target } from '../contract/targetContract';

// ========================================
// Types
// ========================================

export interface TargetManagerModel {
  targets: Target[];
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  deleteTarget: (targetId: string) => Promise<void>;
  activateTarget: (targetId: string) => Promise<void>;
  isDeleting: boolean;
  isActivating: boolean;
  refetch: () => void;
}

// ========================================
// Hook Implementation
// ========================================

export function useTargetManager(): TargetManagerModel {
  const queryClient = useQueryClient();
  const targetService = useTargetService();

  // ========================================
  // Query: ターゲット一覧取得
  // ========================================

  const targetsListQuery = useQuery({
    queryKey: ['targets', 'list'] as const,
    queryFn: () => targetService.getTargetsList(),
    retry: false,
    staleTime: 1000 * 60 * 5, // 5分間キャッシュ
  });

  // ========================================
  // Mutation: ターゲット削除
  // ========================================

  const deleteMutation = useMutation({
    mutationFn: (targetId: string) => targetService.deleteTarget(targetId),
    onSuccess: () => {
      // ターゲット関連のキャッシュを無効化
      queryClient.invalidateQueries({ queryKey: ['targets'] });
    },
  });

  // ========================================
  // Mutation: ターゲットアクティブ化
  // ========================================

  const activateMutation = useMutation({
    mutationFn: (targetId: string) => targetService.activateTarget(targetId),
    onSuccess: () => {
      // ターゲット関連のキャッシュを無効化
      queryClient.invalidateQueries({ queryKey: ['targets'] });
    },
  });

  // ========================================
  // Return Model
  // ========================================

  return {
    // データ
    targets: targetsListQuery.data ?? [],

    // 状態
    isLoading: targetsListQuery.isLoading,
    isError: targetsListQuery.isError,
    error: targetsListQuery.error,

    // アクション
    deleteTarget: deleteMutation.mutateAsync,
    activateTarget: activateMutation.mutateAsync,

    // Mutation状態
    isDeleting: deleteMutation.isPending,
    isActivating: activateMutation.isPending,

    // ユーティリティ
    refetch: targetsListQuery.refetch,
  };
}
