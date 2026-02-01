'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import {
  fetchActiveTarget,
  listTargets,
  createTarget,
  activateTarget,
  deleteTarget,
} from '../api/targetClient';
import {
  type Target,
  type TargetListResponse,
  type CreateTargetRequest,
} from '../contract/targetContract';

export interface TargetManagementPageModelState {
  // UI State
  isCreateModalOpen: boolean;

  // Methods
  openCreateModal: () => void;
  closeCreateModal: () => void;
  handleActivateTarget: (id: string) => Promise<void>;
  handleDeleteTarget: (id: string) => Promise<void>;
  handleCreateTarget: (data: CreateTargetRequest) => Promise<void>;
}

export function useTargetManagementPageModel(): TargetManagementPageModelState & {
  // Queries
  activeTargetQuery: ReturnType<typeof useQuery<Target | null>>;
  targetListQuery: ReturnType<typeof useQuery<TargetListResponse>>;

  // Mutations
  createMutation: ReturnType<typeof useMutation<Target, Error, CreateTargetRequest>>;
  activateMutation: ReturnType<typeof useMutation<Target, Error, string>>;
  deleteMutation: ReturnType<typeof useMutation<void, Error, string>>;
} {
  const queryClient = useQueryClient();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Queries
  const activeTargetQuery = useQuery({
    queryKey: ['targets', 'active'] as const,
    queryFn: () => fetchActiveTarget(),
    retry: false,
  });

  const targetListQuery = useQuery({
    queryKey: ['targets', 'list'] as const,
    queryFn: () => listTargets({ limit: 50 }), // 最大50件取得
    retry: false,
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: createTarget,
    onSuccess: async () => {
      // 作成成功時はリストとアクティブターゲットを更新
      await queryClient.invalidateQueries({ queryKey: ['targets'] });
      setIsCreateModalOpen(false);
    },
  });

  const activateMutation = useMutation({
    mutationFn: activateTarget,
    onSuccess: async () => {
      // 有効化成功時はリストとアクティブターゲットを更新
      await queryClient.invalidateQueries({ queryKey: ['targets'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteTarget,
    onSuccess: async () => {
      // 削除成功時はリストとアクティブターゲットを更新
      await queryClient.invalidateQueries({ queryKey: ['targets'] });
    },
  });

  // Handlers
  const openCreateModal = () => setIsCreateModalOpen(true);
  const closeCreateModal = () => setIsCreateModalOpen(false);

  const handleActivateTarget = async (id: string) => {
    await activateMutation.mutateAsync(id);
  };

  const handleDeleteTarget = async (id: string) => {
    await deleteMutation.mutateAsync(id);
  };

  const handleCreateTarget = async (data: CreateTargetRequest) => {
    await createMutation.mutateAsync(data);
  };

  return {
    // UI State
    isCreateModalOpen,

    // Queries
    activeTargetQuery,
    targetListQuery,

    // Mutations
    createMutation,
    activateMutation,
    deleteMutation,

    // Methods
    openCreateModal,
    closeCreateModal,
    handleActivateTarget,
    handleDeleteTarget,
    handleCreateTarget,
  };
}