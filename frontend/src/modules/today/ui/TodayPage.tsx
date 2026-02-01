'use client';

import { useMemo } from 'react';
import { useSearchParams } from 'next/navigation';

import { TodayPageContent } from './TodayPageContent';

function formatLocalDateYYYYMMDD(d: Date): string {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

export function TodayPage() {
  const searchParams = useSearchParams();

  // URLパラメータから日付を取得（なければ今日）
  const date = useMemo(() => {
    const dateParam = searchParams.get('date');
    if (dateParam && /^\d{4}-\d{2}-\d{2}$/.test(dateParam)) {
      return dateParam;
    }
    return formatLocalDateYYYYMMDD(new Date());
  }, [searchParams]);

  return (
    <div className="w-full space-y-6">
      <div className="space-y-1">
        <div className="text-lg font-semibold">Today</div>
        <div className="text-sm text-muted-foreground">日付: {date}</div>
      </div>

      <TodayPageContent date={date} />
    </div>
  );
}