'use client';

import { useMemo } from 'react';
import { useSearchParams } from 'next/navigation';

import { TodayPageContent } from './TodayPageContent';
import { TodayPageLayout } from './TodayPageLayout';
import { TutorialTrigger } from '@/modules/tutorial';
import { formatLocalDateYYYYMMDD } from '../types/todayTypes';

// ========================================
// Migration Control
// ========================================

// 段階的移行の制御フラグ
const USE_NEW_ARCHITECTURE = process.env.NEXT_PUBLIC_USE_NEW_TODAY_ARCHITECTURE === 'true';

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
            {process.env.NODE_ENV === 'development' && USE_NEW_ARCHITECTURE && (
              <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                NEW
              </span>
            )}
          </div>
          <TutorialTrigger tutorialId="feature_today" className="ml-auto" />
        </div>
        <div className="text-sm text-muted-foreground">日付: {date}</div>
      </div>

      {/* 段階的移行: 新アーキテクチャ or 既存実装 */}
      {USE_NEW_ARCHITECTURE ? (
        <TodayPageLayout date={date} />
      ) : (
        <TodayPageContent date={date} />
      )}
    </div>
  );
}