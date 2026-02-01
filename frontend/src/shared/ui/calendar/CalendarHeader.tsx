'use client';

import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface CalendarHeaderProps {
  year: number;
  month: number; // 1-12
  onPrevMonth: () => void;
  onNextMonth: () => void;
}

export function CalendarHeader({
  year,
  month,
  onPrevMonth,
  onNextMonth,
}: CalendarHeaderProps) {
  // 月名の日本語表示
  const monthNames = [
    '1月', '2月', '3月', '4月', '5月', '6月',
    '7月', '8月', '9月', '10月', '11月', '12月'
  ];

  const monthName = monthNames[month - 1];

  return (
    <div className="flex items-center justify-between">
      {/* 前月ボタン */}
      <Button
        variant="ghost"
        size="sm"
        onClick={onPrevMonth}
        className="h-8 w-8 p-0 hover:bg-gray-100 dark:hover:bg-gray-800"
        aria-label="前月"
      >
        <ChevronLeft className="w-4 h-4" />
      </Button>

      {/* 年月表示 */}
      <div className="flex items-center gap-2">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          {year}年 {monthName}
        </h2>
      </div>

      {/* 次月ボタン */}
      <Button
        variant="ghost"
        size="sm"
        onClick={onNextMonth}
        className="h-8 w-8 p-0 hover:bg-gray-100 dark:hover:bg-gray-800"
        aria-label="次月"
      >
        <ChevronRight className="w-4 h-4" />
      </Button>
    </div>
  );
}