// components/reports/DailyReportPage.tsx
'use client';

import { useRouter } from 'next/navigation';
import { DailyReportHeader } from './DailyReportHeader';
import { DailyReportCard } from './DailyReportCard';
import { ReportActions } from './ReportActions';
import { useDailyReport } from '@/lib/hooks/useDailyReport';

type DailyReportPageProps = {
  date: string; // "YYYY-MM-DD"
};

export function DailyReportPage({ date }: DailyReportPageProps) {
  const router = useRouter();
  const { data, isLoading, error, generate, isGenerating } =
    useDailyReport(date);

  const handleBackToToday = () => router.push('/');
  const handleBackToMeals = () =>
    router.push(`/meals?date=${encodeURIComponent(date)}`);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-64 bg-slate-800/60 rounded-xl animate-pulse" />
        <div className="h-48 bg-slate-900/60 rounded-2xl border border-slate-800 animate-pulse" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="space-y-3">
        <p className="text-sm text-rose-400">
          日次レポートの取得に失敗しました。
        </p>
        <button
          className="text-xs text-emerald-400 underline"
          onClick={() => location.reload()}
        >
          再読み込み
        </button>
      </div>
    );
  }

  const { plan, hasReport, report, isCompleted } = data;

  return (
    <div className="space-y-4 md:space-y-6">
      <DailyReportHeader
        date={date}
        onBackToToday={handleBackToToday}
        onBackToMeals={handleBackToMeals}
      />

      {hasReport && report ? (
        <DailyReportCard report={report} />
      ) : (
        <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 p-4 md:p-5">
          <p className="text-sm text-slate-100 mb-2">
            この日のレポートはまだ生成されていません。
          </p>
          <p className="text-xs text-slate-400">
            1 日の食事記録が完了していれば、「レポートを生成する」ボタンから AI
            による振り返りを作成できます。
          </p>
        </div>
      )}

      <ReportActions
        plan={plan}
        hasReport={hasReport}
        isCompleted={isCompleted}
        isGenerating={isGenerating}
        onGenerate={generate}
        errorMessage={error ? error.message : undefined}
      />
    </div>
  );
}
