/**
 * useProfileManagement - Layer 4: Feature Logic
 *
 * プロフィール管理機能
 *
 * 責務:
 * - プロフィール情報の取得
 * - プロフィールデータのキャッシュ管理
 * - UIに最適化されたインターフェース提供
 */

'use client';

import { useQuery } from '@tanstack/react-query';
import { fetchProfile } from '../api/profileClient';

// ========================================
// Types
// ========================================

export interface ProfileManagementModel {
  profile: Awaited<ReturnType<typeof fetchProfile>> | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => void;
}

// ========================================
// Hook Implementation
// ========================================

export function useProfileManagement(): ProfileManagementModel {
  const profileQuery = useQuery({
    queryKey: ['profile', 'me'] as const,
    queryFn: () => fetchProfile(),
    retry: false,
    staleTime: 1000 * 60 * 5, // 5分間キャッシュ
  });

  return {
    profile: profileQuery.data,
    isLoading: profileQuery.isLoading,
    isError: profileQuery.isError,
    error: profileQuery.error,
    refetch: profileQuery.refetch,
  };
}
