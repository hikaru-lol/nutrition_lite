'use client';

import { cn } from '@/lib/utils';
import type { CalendarDate, CalendarDayData } from './Calendar';

interface CalendarCellProps {
  date: CalendarDate;
  isCurrentMonth: boolean;
  isToday: boolean;
  isSelected: boolean;
  dayData?: CalendarDayData;
  onClick: () => void;
}

export function CalendarCell({
  date,
  isCurrentMonth,
  isToday,
  isSelected,
  dayData,
  onClick,
}: CalendarCellProps) {
  // インジケーター用のスタイル計算
  const getGoalAchievementColor = (percentage?: number) => {
    if (!percentage) return '';
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const hasMeals = dayData?.hasMeals || false;
  const hasReport = dayData?.hasReport || false;
  const goalPercentage = dayData?.goalAchievementPercentage;

  return (
    <button
      onClick={onClick}
      className={cn(
        'relative w-full h-10 p-1 text-sm font-medium rounded-md transition-all duration-200 hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
        // 月の表示状態
        isCurrentMonth
          ? 'text-gray-900 dark:text-gray-100'
          : 'text-gray-400 dark:text-gray-600',
        // 今日の強調
        isToday && 'bg-blue-100 dark:bg-blue-900/30 text-blue-900 dark:text-blue-100 font-bold',
        // 選択状態
        isSelected && 'bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700',
        // 日曜日の色
        (date.day % 7 === 1 || new Date(date.year, date.month - 1, date.day).getDay() === 0) &&
          !isSelected &&
          !isToday &&
          'text-red-600 dark:text-red-400',
        // 土曜日の色
        new Date(date.year, date.month - 1, date.day).getDay() === 6 &&
          !isSelected &&
          !isToday &&
          'text-blue-600 dark:text-blue-400'
      )}
    >
      {/* 日付表示 */}
      <span className="relative z-10">{date.day}</span>

      {/* インジケーター */}
      <div className="absolute bottom-0.5 left-1/2 transform -translate-x-1/2 flex gap-0.5">
        {/* 食事記録インジケーター */}
        {hasMeals && (
          <div
            className="w-1.5 h-1.5 rounded-full bg-green-600"
            title="食事記録あり"
          />
        )}

        {/* 目標達成度インジケーター */}
        {goalPercentage !== undefined && (
          <div
            className={cn(
              'w-1.5 h-1.5 rounded-full',
              getGoalAchievementColor(goalPercentage)
            )}
            title={`目標達成度: ${goalPercentage}%`}
          />
        )}

        {/* レポート生成済みインジケーター */}
        {hasReport && (
          <div
            className="w-1.5 h-1.5 rounded-full bg-purple-600"
            title="レポート生成済み"
          />
        )}
      </div>

      {/* 選択・今日のオーバーレイ */}
      {(isSelected || isToday) && (
        <div
          className={cn(
            'absolute inset-0 rounded-md pointer-events-none',
            isSelected
              ? 'ring-2 ring-blue-600 ring-inset'
              : isToday
              ? 'ring-2 ring-blue-300 ring-inset'
              : ''
          )}
        />
      )}
    </button>
  );
}