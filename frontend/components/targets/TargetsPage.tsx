// frontend/components/targets/TargetsPage.tsx
'use client';

import { useEffect, useState } from 'react';
import { PageHeader } from '@/components/layout/PageHeader';
import { Button } from '@/components/ui/button';
import {
  fetchTargets,
  createTarget,
  activateTarget,
  type TargetResponseApi,
} from '@/lib/api/targets';
import { ApiError } from '@/lib/api/client';
import { TargetCard } from './TargetCard';
import {
  CreateTargetForm,
  type CreateTargetFormValues,
} from './CreateTargetForm';

export function TargetsPage() {
  const [targets, setTargets] = useState<TargetResponseApi[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [serverError, setServerError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        setIsLoading(true);
        setServerError(null);
        const items = await fetchTargets();
        setTargets(items);
      } catch (e: any) {
        console.error('Failed to fetch targets', e);
        setServerError(e?.message ?? 'ターゲットの取得に失敗しました。');
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  const refresh = async () => {
    try {
      const items = await fetchTargets();
      setTargets(items);
    } catch (e) {
      console.error('Failed to refresh targets', e);
    }
  };

  const handleCreateSubmit = async (values: CreateTargetFormValues) => {
    try {
      setIsCreating(true);
      setServerError(null);

      await createTarget({
        title: values.title,
        goal_type: values.goal_type,
        activity_level: values.activity_level,
        goal_description: values.goal_description || undefined,
      });

      setShowCreateForm(false);
      await refresh();
    } catch (e: any) {
      console.error('Failed to create target', e);
      if (e instanceof ApiError && e.status === 409) {
        setServerError('ターゲットの上限（5件）に達しています。');
      } else {
        setServerError(e?.message ?? 'ターゲットの作成に失敗しました。');
      }
    } finally {
      setIsCreating(false);
    }
  };

  const handleActivate = async (targetId: string) => {
    try {
      setServerError(null);
      await activateTarget(targetId);
      await refresh();
    } catch (e: any) {
      console.error('Failed to activate target', e);
      setServerError(e?.message ?? 'ターゲットの切り替えに失敗しました。');
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <PageHeader title="ターゲット" />
        <p className="text-sm text-slate-400">読み込み中...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 md:space-y-6">
      <PageHeader
        title="ターゲット"
        description="栄養の目標パターンを管理し、アクティブなターゲットを切り替えることができます。"
        actions={
          <Button
            size="sm"
            onClick={() => setShowCreateForm((v) => !v)}
            variant={showCreateForm ? 'secondary' : 'primary'}
          >
            {showCreateForm ? '作成フォームを閉じる' : '新しいターゲットを作成'}
          </Button>
        }
      />

      {serverError && (
        <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/40 rounded-lg px-3 py-2">
          {serverError}
        </p>
      )}

      {showCreateForm && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 md:p-5">
          <h2 className="text-sm font-semibold text-slate-50 mb-2">
            新しいターゲットを作成
          </h2>
          <p className="text-xs text-slate-400 mb-4">
            現在の体格・活動量に合わせて、AIが1日の栄養バランスを自動で提案します。目標や活動レベルを指定してください。
          </p>
          <CreateTargetForm
            onSubmit={handleCreateSubmit}
            onCancel={() => setShowCreateForm(false)}
            isSubmitting={isCreating}
            serverError={null}
          />
        </div>
      )}

      <div className="grid gap-3 md:grid-cols-2">
        {targets.length === 0 ? (
          <p className="text-sm text-slate-400">
            まだターゲットが登録されていません。「新しいターゲットを作成」から最初のターゲットを作成してみましょう。
          </p>
        ) : (
          targets.map((t) => (
            <TargetCard
              key={t.id}
              target={t}
              onActivate={() => handleActivate(t.id)}
            />
          ))
        )}
      </div>
    </div>
  );
}
