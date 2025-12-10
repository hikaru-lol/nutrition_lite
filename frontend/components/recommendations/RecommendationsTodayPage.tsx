// frontend/components/recommendations/RecommendationsTodayPage.tsx
'use client';

import { useTodayRecommendation } from '@/lib/hooks/useTodayRecommendation';
import { PageHeader } from '@/components/layout/PageHeader';
import { RecommendationCard } from '@/components/recommendations/RecommendationCard';
import { RecommendationEmptyState } from '@/components/recommendations/RecommendationEmptyState';
import { PlanRestrictionNotice } from '@/components/recommendations/PlanRestrictionNotice';

export function RecommendationsTodayPage() {
  const { data, isLoading, error } = useTodayRecommendation();

  if (isLoading) {
    return (
      <div className="space-y-4">
        <PageHeader title="今日の提案" />
        <div className="h-40 rounded-2xl border border-slate-800 bg-slate-900/60 animate-pulse" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="space-y-4">
        <PageHeader title="今日の提案" />
        <p className="text-sm text-rose-400">
          提案の取得に失敗しました。時間をおいて再度お試しください。
        </p>
      </div>
    );
  }

  const { plan, hasRecommendation, recommendation } = data;

  return (
    <div className="space-y-4 md:space-y-6">
      <PageHeader
        title="今日の提案"
        description="直近の食事傾向をもとに、次に意識すると良いポイントを提案します。"
      />

      {plan === 'free' ? (
        <PlanRestrictionNotice />
      ) : hasRecommendation && recommendation ? (
        <RecommendationCard recommendation={recommendation} />
      ) : (
        <RecommendationEmptyState />
      )}
    </div>
  );
}
