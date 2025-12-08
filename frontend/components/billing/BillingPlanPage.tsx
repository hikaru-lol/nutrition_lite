// frontend/components/billing/BillingPlanPage.tsx
'use client';

import { useState } from 'react';
import { useCurrentUser } from '@/lib/hooks/useCurrentUser';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { fetchBillingPortalUrl } from '@/lib/api/billing';

export function BillingPlanPage() {
  const { user, isLoading } = useCurrentUser();
  const [isRedirecting, setIsRedirecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (isLoading || !user) {
    return (
      <div className="space-y-4">
        <PageHeader title="プラン" />
        <p className="text-sm text-slate-400">読み込み中...</p>
      </div>
    );
  }

  const handleOpenPortal = async () => {
    try {
      setIsRedirecting(true);
      setError(null);
      const url = await fetchBillingPortalUrl();
      window.location.href = url;
    } catch (e: any) {
      console.error('Failed to open billing portal', e);
      setError(
        e?.message ??
          '支払い情報管理ページの表示に失敗しました。時間をおいて再度お試しください。'
      );
      setIsRedirecting(false);
    }
  };

  return (
    <div className="space-y-4 md:space-y-6">
      <PageHeader
        title="現在のプラン"
        description="プランの状態と支払い情報を確認できます。"
      />

      {error && (
        <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/40 rounded-lg px-3 py-2">
          {error}
        </p>
      )}

      <Card>
        <p className="text-sm text-slate-100 mb-1">
          プラン: {user.plan.toUpperCase()}
        </p>
        {user.plan === 'trial' && user.trialEndsAt && (
          <p className="text-xs text-slate-400 mb-2">
            トライアル終了予定日: {user.trialEndsAt}
          </p>
        )}
        <p className="text-xs text-slate-400 mb-4">
          有料プランではすべての機能が利用できます。プランの変更や支払い方法の更新は、以下のボタンから行えます。
        </p>
        <Button
          size="sm"
          variant="secondary"
          onClick={handleOpenPortal}
          disabled={isRedirecting}
        >
          {isRedirecting ? '遷移中...' : '支払い情報を管理する'}
        </Button>
      </Card>
    </div>
  );
}
