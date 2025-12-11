// components/reports/DailyReportCard.tsx
import { Card } from '@/components/ui/card';
import type { DailyReportVM } from '@/lib/hooks/useDailyReport';
import { ReportSection } from './ReportSection';

type DailyReportCardProps = {
  report: DailyReportVM;
};

export function DailyReportCard({ report }: DailyReportCardProps) {
  const { summary, goodPoints, improvementPoints, tomorrowFocus } = report;

  return (
    <Card>
      <div className="mb-4">
        <p className="text-xs text-slate-400 mb-1">全体のまとめ</p>
        <p className="text-sm md:text-base text-slate-100 whitespace-pre-line">
          {summary}
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <ReportSection title="よかった点" variant="good" items={goodPoints} />
        <ReportSection
          title="改善ポイント"
          variant="improvement"
          items={improvementPoints}
        />
        <ReportSection
          title="明日のフォーカス"
          variant="focus"
          items={tomorrowFocus}
        />
      </div>
    </Card>
  );
}
