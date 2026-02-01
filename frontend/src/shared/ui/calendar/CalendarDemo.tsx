'use client';

import { Calendar } from './Calendar';
import { useCalendarModel } from '@/modules/calendar';

/**
 * カレンダーコンポーネントのデモ・テスト用
 * Phase 2でカレンダーページ実装時に参考にする
 */
export function CalendarDemo() {
  const {
    selectedDate,
    viewingYear,
    viewingMonth,
    dayData,
    handleDateSelect,
    handleMonthChange,
    isLoading,
  } = useCalendarModel();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-sm text-gray-600">カレンダーを読み込み中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <Calendar
        selectedDate={selectedDate}
        onDateSelect={handleDateSelect}
        onMonthChange={handleMonthChange}
        dayData={dayData}
      />

      {/* デバッグ情報 */}
      <div className="text-xs text-gray-500 p-4 bg-gray-50 rounded-md dark:bg-gray-900 dark:text-gray-400">
        <p>選択日: {selectedDate.year}年{selectedDate.month}月{selectedDate.day}日</p>
        <p>表示中: {viewingYear}年{viewingMonth}月</p>
        <p>日付データ件数: {dayData.length}件</p>
      </div>
    </div>
  );
}