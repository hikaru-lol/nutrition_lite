// components/reports/DailyReportHeader.tsx
'use client';

import { PageHeader } from '@/components/layout/PageHeader';
import { Button } from '@/components/ui/button';

type DailyReportHeaderProps = {
  date: string; // "YYYY-MM-DD"
  onBackToToday: () => void;
  onBackToMeals: () => void;
};

export function DailyReportHeader({
  date,
  onBackToToday,
  onBackToMeals,
}: DailyReportHeaderProps) {
  const title = formatDateJP(new Date(date));

  return (
    <PageHeader
      title={`${title} の日次レポート`}
      description="この日はどんな食事になっていたか、栄養の観点から振り返ってみましょう。"
      actions={
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={onBackToMeals}>
            食事記録を見る
          </Button>
          <Button variant="secondary" size="sm" onClick={onBackToToday}>
            Today に戻る
          </Button>
        </div>
      }
    />
  );
}

function formatDateJP(date: Date) {
  const y = date.getFullYear();
  const m = date.getMonth() + 1;
  const d = date.getDate();
  const w = ['日', '月', '火', '水', '木', '金', '土'][date.getDay()];
  return `${y}年${m}月${d}日(${w})`;
}
