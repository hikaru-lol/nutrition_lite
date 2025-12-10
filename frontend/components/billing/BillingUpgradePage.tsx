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

  const handleBackToPlan = () => {
    router.push('/billing/plan');
  };

  const isPaid = user.plan === 'paid';

  return (
    <div className="space-y-4 md:space-y-6">
      <PageHeader
        title="プランのアップグレード"
        description="有料プランにアップグレードすると、レポートや提案機能を継続してご利用いただけます。"
        actions={
          <Button variant="ghost" size="sm" onClick={handleBackToPlan}>
            プラン概要に戻る
          </Button>
        }
      />

      {error && (
        <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/40 rounded-lg px-3 py-2">
          {error}
        </p>
      )}

      <Card className="space-y-4">
        <div>
          <p className="text-xs text-slate-400 mb-1">現在のプラン</p>
          <p className="text-lg font-semibold text-slate-50">
            {user.plan.toUpperCase()}
          </p>
          {user.plan === 'trial' && user.trialEndsAt && (
            <p className="mt-1 text-xs text-amber-300/80">
              トライアル終了予定日: {user.trialEndsAt}
            </p>
          )}
        </div>

        <div className="border-t border-slate-800 pt-3">
          <p className="text-xs text-slate-400 mb-2">
            有料プランにアップグレードすると、次のような機能が利用できます：
          </p>
          <ul className="space-y-1 text-xs text-slate-200">
            <li>・1日の食事から自動生成される日次レポート</li>
            <li>・直近の傾向に基づいた具体的な食事提案</li>
            <li>・ターゲットや記録を使った継続的な振り返り</li>
            <li>・将来的な機能追加（習慣化サポート、さらに高度な分析など）</li>
          </ul>
        </div>

        <div className="pt-2 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          {isPaid ? (
            <p className="text-xs text-emerald-400">
              すでに有料プランをご利用中です。プランの変更や解約は、支払い情報管理ページから行えます。
            </p>
          ) : (
            <p className="text-xs text-slate-400">
              今すぐアップグレードして、記録から得られるフィードバックを最大限に活かしましょう。
            </p>
          )}

          <Button onClick={handleUpgrade} disabled={isRedirecting || isPaid}>
            {isPaid
              ? 'すでに有料プランです'
              : isRedirecting
              ? '決済ページへ遷移中...'
              : '有料プランにアップグレード'}
          </Button>
        </div>
      </Card>
    </div>
  );
}
