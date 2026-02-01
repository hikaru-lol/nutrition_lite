'use client';

import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

import { useTargetManagementPageModel } from '../model/useTargetManagementPageModel';
import { ActiveTargetCard } from './ActiveTargetCard';
import { TargetListCard } from './TargetListCard';
import { CreateTargetModal } from './CreateTargetModal';

export function TargetManagementPage() {
  const m = useTargetManagementPageModel();

  const activeTarget = m.activeTargetQuery.data ?? null;
  const targetList = m.targetListQuery.data?.items ?? [];

  const isLoadingActive = m.activeTargetQuery.isLoading;
  const isLoadingList = m.targetListQuery.isLoading;

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
        <Button onClick={m.openCreateModal} className="gap-2">
          <Plus className="h-4 w-4" />
          新規作成
        </Button>
      </div>

      {/* メインコンテンツ */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左側: アクティブターゲット詳細 */}
        <div className="lg:col-span-2">
          <ActiveTargetCard
            target={activeTarget}
            isLoading={isLoadingActive}
          />
        </div>

        {/* 右側: 新規作成ボタン（モバイル時は非表示） */}
        <div className="hidden lg:block">
          <div className="sticky top-4">
            <div className="border-2 border-dashed border-muted-foreground/30 rounded-lg p-8 text-center hover:border-muted-foreground/50 transition-colors">
              <Plus className="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
              <p className="text-sm font-medium mb-2">新しいターゲット</p>
              <p className="text-xs text-muted-foreground mb-4">
                目標に応じて栄養ターゲットを自動生成
              </p>
              <Button onClick={m.openCreateModal} variant="outline" size="sm">
                作成する
              </Button>
            </div>
          </div>
        </div>

        {/* 下部: ターゲット一覧 */}
        <div className="lg:col-span-3">
          <TargetListCard
            targets={targetList}
            activeTargetId={activeTarget?.id ?? null}
            isLoading={isLoadingList}
            isActivating={m.activateMutation.isPending}
            isDeleting={m.deleteMutation.isPending}
            onActivate={m.handleActivateTarget}
            onDelete={m.handleDeleteTarget}
          />
        </div>
      </div>

      {/* ターゲット作成モーダル */}
      <CreateTargetModal
        isOpen={m.isCreateModalOpen}
        onClose={m.closeCreateModal}
        onSubmit={m.handleCreateTarget}
        isLoading={m.createMutation.isPending}
        error={
          m.createMutation.isError
            ? m.createMutation.error instanceof Error
              ? m.createMutation.error.message
              : 'ターゲットの作成に失敗しました'
            : null
        }
      />

      {/* エラー表示 */}
      {m.activateMutation.isError && (
        <div className="fixed bottom-4 right-4 bg-destructive text-destructive-foreground p-3 rounded-md shadow-lg">
          ターゲットの有効化に失敗しました
        </div>
      )}

      {m.deleteMutation.isError && (
        <div className="fixed bottom-4 right-4 bg-destructive text-destructive-foreground p-3 rounded-md shadow-lg">
          ターゲットの削除に失敗しました
        </div>
      )}
    </div>
  );
}