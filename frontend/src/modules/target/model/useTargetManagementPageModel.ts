'use client';

import { useActiveTargetQuery } from '../hooks/useActiveTargetQuery';
import { useTargetManager } from '../hooks/useTargetManager';
import { useCreateTargetMutation } from '../hooks/useCreateTargetMutation';
import type { Target, CreateTargetRequest } from '../contract/targetContract';

export interface TargetManagementPageModel {
  // Data
  activeTarget: Target | null;
  targetList: Target[];

  // State - Active Target
  isLoadingActive: boolean;
  isErrorActive: boolean;

  // State - Target List
  isLoadingList: boolean;
  isErrorList: boolean;

  // Create
  createTarget: (data: CreateTargetRequest) => Promise<Target>;
  isCreating: boolean;
  isCreateError: boolean;
  createError: Error | null;

  // Activate
  activateTarget: (id: string) => Promise<void>;
  isActivating: boolean;

  // Delete
  deleteTarget: (id: string) => Promise<void>;
  isDeleting: boolean;

  // Refetch
  refetch: () => void;
}

export function useTargetManagementPageModel(): TargetManagementPageModel {
  // Layer 4 フックを組み合わせる
  const activeTargetQuery = useActiveTargetQuery();
  const targetManager = useTargetManager();
  const createTargetMutation = useCreateTargetMutation();

  return {
    // Data
    activeTarget: activeTargetQuery.activeTarget,
    targetList: targetManager.targets,

    // State - Active Target
    isLoadingActive: activeTargetQuery.isLoading,
    isErrorActive: activeTargetQuery.isError,

    // State - Target List
    isLoadingList: targetManager.isLoading,
    isErrorList: targetManager.isError,

    // Create
    createTarget: createTargetMutation.createTarget,
    isCreating: createTargetMutation.isPending,
    isCreateError: createTargetMutation.isError,
    createError: createTargetMutation.error,

    // Activate
    activateTarget: targetManager.activateTarget,
    isActivating: targetManager.isActivating,

    // Delete
    deleteTarget: targetManager.deleteTarget,
    isDeleting: targetManager.isDeleting,

    // Refetch
    refetch: () => {
      activeTargetQuery.refetch();
      targetManager.refetch();
    },
  };
}