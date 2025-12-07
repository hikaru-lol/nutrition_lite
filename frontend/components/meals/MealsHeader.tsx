'use client';

import { PageHeader } from '@/components/layout/PageHeader';
import { Button } from '@/components/ui/button';

type MealsHeaderProps = {
  date: string; // "YYYY-MM-DD"
  onChangeDate: (newDate: string) => void;
  onBackToToday: () => void;
};

export function MealsHeader({
  date,
  onChangeDate,
  onBackToToday,
}: MealsHeaderProps) {
  const current = new Date(date);

  const shiftDate = (days: number) => {
    const d = new Date(current);
    d.setDate(d.getDate() + days);
    const iso = d.toISOString().slice(0, 10);
    onChangeDate(iso);
  };

  const title = formatDateJP(current);

  return (
    <PageHeader
      title={`${title} の食事記録`}
      description="1日の食事内容を記録・振り返ることができます。"
      actions={
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={() => shiftDate(-1)}>
            前日
          </Button>
          <Button variant="ghost" size="sm" onClick={() => shiftDate(1)}>
            翌日
          </Button>
          <Button variant="secondary" size="sm" onClick={onBackToToday}>
            今日に戻る
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
