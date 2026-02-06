'use client';

import { useMemo } from 'react';
import { useSearchParams } from 'next/navigation';

import { TodayPageContent } from './TodayPageContent';
import { TutorialTrigger } from '@/modules/tutorial';
import { formatLocalDateYYYYMMDD } from '../types/todayTypes';

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
        <div className="flex items-center gap-2">
          <div className="text-lg font-semibold" data-tour="today-title">
            Today
          </div>
          <TutorialTrigger tutorialId="feature_today" className="ml-auto" />
        </div>
        <div className="text-sm text-muted-foreground">日付: {date}</div>
      </div>

      <TodayPageContent date={date} />
    </div>
  );
}