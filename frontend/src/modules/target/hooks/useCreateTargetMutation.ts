/**
 * useCreateTargetMutation - Layer 4: Feature Logic
 *
 * ターゲット作成
 *
 * 責務:
 * - ターゲット作成の Mutation
 * - キャッシュの無効化
 */

'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useTargetService } from '../services/targetService';
import type { Target, CreateTargetRequest } from '../contract/targetContract';

// ========================================
// Types
// ========================================

export interface CreateTargetMutationModel {
  createTarget: (data: CreateTargetRequest) => Promise<Target>;
  isPending: boolean;
  isError: boolean;
  error: Error | null;
}

// ========================================
// Hook Implementation
// ========================================

export function useCreateTargetMutation(): CreateTargetMutationModel {
  const queryClient = useQueryClient();
  const targetService = useTargetService();

  const mutation = useMutation({
    mutationFn: (data: CreateTargetRequest) => targetService.createTarget(data),
    onSuccess: () => {
      // ターゲット関連のキャッシュを無効化
      queryClient.invalidateQueries({ queryKey: ['targets'] });
    },
  });

  return {
    createTarget: mutation.mutateAsync,
    isPending: mutation.isPending,
    isError: mutation.isError,
    error: mutation.error,
  };
}
