/**
 * useActiveTargetQuery - Layer 4: Feature Logic
 *
 * アクティブなターゲットの取得
 *
 * 責務:
 * - アクティブターゲットのデータ取得
 * - React Query による状態管理
 */

'use client';

import { useQuery } from '@tanstack/react-query';
import { useTargetService } from '../services/targetService';
import type { Target } from '../contract/targetContract';

// ========================================
// Types
// ========================================

export interface ActiveTargetQueryModel {
  activeTarget: Target | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => void;
}

// ========================================
// Hook Implementation
// ========================================

export function useActiveTargetQuery(): ActiveTargetQueryModel {
  const targetService = useTargetService();

  const query = useQuery({
    queryKey: ['targets', 'active'] as const,
    queryFn: () => targetService.getActiveTarget(),
    retry: false,
    staleTime: 1000 * 60 * 5, // 5分間キャッシュ
  });

  return {
    activeTarget: query.data ?? null,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}
