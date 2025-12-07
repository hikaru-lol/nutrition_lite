'use client';

import { useRouter } from 'next/navigation';
import { useTodayOverview } from '@/lib/hooks/useTodayOverview';
import { TodayHeader } from './TodayHeader';
import { TodayProgressCard } from './TodayProgressCard';
import { TodayMealsSummaryCard } from './TodayMealsSummaryCard';
import { TodayReportPreviewCard } from './TodayReportPreviewCard';
import { TodayRecommendationPreviewCard } from './TodayRecommendationPreviewCard';
import { UpgradeBanner } from '@/components/common/UpgradeBanner';

export function TodayPage() {
  const router = useRouter();
  const { data, isLoading, error } = useTodayOverview();

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-10 w-48 bg-slate-800/60 rounded-xl animate-pulse" />
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <div className="h-40 bg-slate-900/60 rounded-2xl border border-slate-800 animate-pulse" />
          <div className="h-40 bg-slate-900/60 rounded-2xl border border-slate-800 animate-pulse" />
          <div className="h-40 bg-slate-900/60 rounded-2xl border border-slate-800 animate-pulse hidden xl:block" />
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="space-y-3">
        <p className="text-sm text-rose-400">データの取得に失敗しました。</p>
        <button
          className="text-xs text-emerald-400 underline"
          onClick={() => location.reload()}
        >
          再読み込み
        </button>
      </div>
    );
  }

  const {
    userName,
    plan,
    trialEndsAt,
    progress,
    mealsSummary,
    reportPreview,
    recommendationPreview,
  } = data;

  const navigateToMeals = () =>
    router.push(`/meals?date=${encodeURIComponent(progress.date)}`);

  const navigateToReport = () =>
    router.push(`/reports/daily/${encodeURIComponent(progress.date)}`);

  const navigateToRecommendation = () => router.push(`/recommendations/today`);

  const navigateToUpgrade = () => router.push('/billing/upgrade');

  return (
    <div className="space-y-6">
      <TodayHeader userName={userName} plan={plan} trialEndsAt={trialEndsAt} />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <TodayProgressCard
          progress={progress}
          onNavigateToMeals={navigateToMeals}
          onNavigateToReport={navigateToReport}
        />
        <TodayMealsSummaryCard
          mealsSummary={mealsSummary}
          onNavigateToMeals={navigateToMeals}
        />
        <div className="space-y-4">
          <TodayReportPreviewCard
            report={reportPreview}
            isCompleted={progress.isCompleted}
            plan={plan}
            onNavigateToReport={navigateToReport}
            onNavigateToUpgrade={navigateToUpgrade}
          />
          <TodayRecommendationPreviewCard
            recommendation={recommendationPreview}
            plan={plan}
            onNavigateToRecommendation={navigateToRecommendation}
            onNavigateToUpgrade={navigateToUpgrade}
          />
        </div>
      </div>

      {(plan === 'trial' || plan === 'free') && (
        <UpgradeBanner
          plan={plan}
          trialEndsAt={trialEndsAt}
          onUpgradeClick={navigateToUpgrade}
        />
      )}
    </div>
  );
}
