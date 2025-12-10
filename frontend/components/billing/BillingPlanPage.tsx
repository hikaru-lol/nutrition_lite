// frontend/components/billing/BillingPlanPage.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useCurrentUser } from '@/lib/hooks/useCurrentUser';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { fetchBillingPortalUrl } from '@/lib/api/billing';

export function BillingPlanPage() {
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

  const handleGotoUpgrade = () => {
    router.push('/billing/upgrade');
  };

  const planLabel = user.plan.toUpperCase();

  return (
    <div className="space-y-4 md:space-y-6">
      <PageHeader
        title="現在のプラン"
        description="ご利用中のプランと、プランに含まれる機能を確認できます。"
      />

      {error && (
        <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/40 rounded-lg px-3 py-2">
          {error}
        </p>
      )}

      <Card className="space-y-3">
        <div>
          <p className="text-xs text-slate-400 mb-1">プラン</p>
          <p className="text-lg font-semibold text-slate-50">{planLabel}</p>
          {user.plan === 'trial' && user.trialEndsAt && (
            <p className="mt-1 text-xs text-amber-300/80">
              トライアル終了予定日: {user.trialEndsAt}
            </p>
          )}
        </div>

        <div className="border-t border-slate-800 pt-3 space-y-1">
          <p className="text-xs text-slate-400">利用可能な主な機能</p>
          <ul className="mt-1 space-y-1 text-xs text-slate-200">
            <li>・食事記録（FoodEntry）の登録・編集</li>
            {user.plan !== 'free' && (
              <>
                <li>・1日の栄養サマリ（Daily Nutrition Summary）の自動計算</li>
                <li>・日次レポート（DailyNutritionReport）の生成・閲覧</li>
                <li>・直近の傾向に基づく提案（MealRecommendation）</li>
              </>
            )}
            {user.plan === 'free' && (
              <>
                <li className="line-through text-slate-500">
                  ・日次レポートの自動生成
                </li>
                <li className="line-through text-slate-500">
                  ・食事提案（レコメンド）機能
                </li>
              </>
            )}
          </ul>
        </div>

        <div className="pt-2 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          {user.plan === 'paid' ? (
            <p className="text-xs text-emerald-400">
              現在、有料プランをご利用中です。いつでも支払い情報を確認・変更できます。
            </p>
          ) : (
            <p className="text-xs text-slate-400">
              有料プランにアップグレードすると、日次レポートや提案機能など、すべての機能が利用可能になります。
            </p>
          )}

          <div className="flex gap-2 justify-end">
            {user.plan !== 'paid' && (
              <Button size="sm" variant="primary" onClick={handleGotoUpgrade}>
                プランをアップグレード
              </Button>
            )}
            <Button
              size="sm"
              variant="secondary"
              onClick={handleOpenPortal}
              disabled={isRedirecting}
            >
              {isRedirecting ? '遷移中...' : '支払い情報を管理する'}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
