// frontend/components/targets/TargetsPage.tsx
'use client';

import { useEffect, useState } from 'react';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  fetchTargets,
  createTarget,
  activateTarget,
  type TargetResponseApi,
  type GoalType,
  type ActivityLevel,
} from '@/lib/api/targets';
import { ApiError } from '@/lib/api/client';

export function TargetsPage() {
  const [targets, setTargets] = useState<TargetResponseApi[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [serverError, setServerError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);

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

  const handleCreateSimpleTarget = async () => {
    // とりあえず固定値の goal_type/activity_level で 1 個作る例
    const title = 'デフォルトターゲット';
    const goal_type: GoalType = 'maintain';
    const activity_level: ActivityLevel = 'normal';

    try {
      setIsCreating(true);
      await createTarget({
        title,
        goal_type,
        activity_level,
      });
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
            onClick={handleCreateSimpleTarget}
            disabled={isCreating}
          >
            {isCreating ? '作成中...' : '新しいターゲットを作成'}
          </Button>
        }
      />

      {serverError && (
        <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/40 rounded-lg px-3 py-2">
          {serverError}
        </p>
      )}

      <div className="grid gap-3 md:grid-cols-2">
        {targets.length === 0 ? (
          <p className="text-sm text-slate-400">
            まだターゲットが登録されていません。「新しいターゲットを作成」を押して開始しましょう。
          </p>
        ) : (
          targets.map((t) => (
            <Card key={t.id} className="space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-50">
                    {t.title}
                  </p>
                  <p className="text-xs text-slate-400">
                    目標: {t.goal_type} / 活動レベル: {t.activity_level}
                  </p>
                </div>
                {t.is_active && (
                  <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/40">
                    アクティブ
                  </span>
                )}
              </div>
              <Button
                size="sm"
                variant="secondary"
                disabled={t.is_active}
                onClick={() => handleActivate(t.id)}
              >
                {t.is_active ? '現在のターゲット' : 'このターゲットを使う'}
              </Button>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
