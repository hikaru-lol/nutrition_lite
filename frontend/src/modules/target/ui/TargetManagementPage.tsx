'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

import { useTargetManagementPageModel } from '../model/useTargetManagementPageModel';
import type { CreateTargetRequest } from '../contract/targetContract';
import { ActiveTargetCard } from './ActiveTargetCard';
import { TargetListCard } from './TargetListCard';
import { CreateTargetModal } from './CreateTargetModal';

export function TargetManagementPage() {
  const {
    activeTarget,
    targetList,
    isLoadingActive,
    isLoadingList,
    createTarget,
    isCreating,
    createError,
    activateTarget,
    isActivating,
    deleteTarget,
    isDeleting,
  } = useTargetManagementPageModel();

  // UI 状態管理 (Layer 2)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // ========================================
  // Event Handlers
  // ========================================

  const handleCreateTarget = async (data: CreateTargetRequest) => {
    await createTarget(data);
    setIsCreateModalOpen(false); // 成功時にモーダルを閉じる
  };

  return (
    <div className="w-full space-y-6">
      {/* ページヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">ターゲット管理</h1>
          <p className="text-muted-foreground">
            栄養目標の作成・管理・切り替えを行えます
          </p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)} className="gap-2">
          <Plus className="h-4 w-4" />
          新規作成
        </Button>
      </div>

      {/* メインコンテンツ */}
      <div className="space-y-6">
        {/* アクティブターゲット詳細 */}
        <ActiveTargetCard
          target={activeTarget}
          isLoading={isLoadingActive}
        />

        {/* ターゲット一覧 */}
        <TargetListCard
          targets={targetList}
          activeTargetId={activeTarget?.id ?? null}
          isLoading={isLoadingList}
          isActivating={isActivating}
          isDeleting={isDeleting}
          onActivate={activateTarget}
          onDelete={deleteTarget}
        />
      </div>

      {/* ターゲット作成モーダル */}
      <CreateTargetModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateTarget}
        isLoading={isCreating}
        error={createError?.message ?? null}
      />
    </div>
  );
}