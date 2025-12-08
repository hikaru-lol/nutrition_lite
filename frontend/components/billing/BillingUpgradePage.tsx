// frontend/components/billing/BillingUpgradePage.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useCurrentUser } from '@/lib/hooks/useCurrentUser';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { createCheckoutSession } from '@/lib/api/billing';

export function BillingUpgradePage() {
  const router = useRouter();
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

  const handleUpgrade = async () => {
    try {
      setIsRedirecting(true);
      setError(null);
      const url = await createCheckoutSession();
      window.location.href = url;
    } catch (e: any) {
      console.error('Failed to create checkout session', e);
      setError(
        e?.message ??
          '決済ページの作成に失敗しました。時間をおいて再度お試しください。'
      );
      setIsRedirecting(false);
    }
  };

  return (
    <div className="space-y-4 md:space-y-6">
      <PageHeader
        title="プランのアップグレード"
        description="有料プランにアップグレードすると、提案機能や高度なレポートを継続して利用できます。"
      />

      {error && (
        <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/40 rounded-lg px-3 py-2">
          {error}
        </p>
      )}

      <Card>
        <p className="text-sm text-slate-100 mb-2">
          現在のプラン: {user.plan.toUpperCase()}
        </p>
        {user.plan === 'trial' && user.trialEndsAt && (
          <p className="text-xs text-slate-400 mb-2">
            トライアル終了予定日: {user.trialEndsAt}
          </p>
        )}
        <p className="text-xs text-slate-400 mb-4">
          有料プランでは、日次レポート・提案機能・将来的な高度な分析機能が利用可能になります。
        </p>
        <Button
          onClick={handleUpgrade}
          disabled={isRedirecting || user.plan === 'paid'}
        >
          {user.plan === 'paid'
            ? 'すでに有料プランです'
            : isRedirecting
            ? '決済ページへ遷移中...'
            : '有料プランにアップグレード'}
        </Button>
      </Card>
    </div>
  );
}
