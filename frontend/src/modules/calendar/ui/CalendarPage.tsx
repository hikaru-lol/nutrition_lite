'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useMemo } from 'react';
import { Calendar as CalendarIcon, ArrowLeft } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Calendar } from '@/shared/ui/calendar';
import { useCalendarModel } from '@/modules/calendar';
import { TodayPageContent } from '@/modules/today/ui/TodayPageContent';
import { TutorialTrigger } from '@/modules/tutorial';

function parseCalendarDate(dateString: string) {
  const [year, month, day] = dateString.split('-').map(Number);
  return { year, month, day };
}

function formatCalendarDate(date: { year: number; month: number; day: number }): string {
  return `${date.year}-${String(date.month).padStart(2, '0')}-${String(date.day).padStart(2, '0')}`;
}

export function CalendarPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // URLパラメータから初期日付を取得
  const initialDate = useMemo(() => {
    const dateParam = searchParams.get('date');
    if (dateParam) {
      try {
        return parseCalendarDate(dateParam);
      } catch {
        // 無効な日付の場合は今日を使用
        const today = new Date();
        return {
          year: today.getFullYear(),
          month: today.getMonth() + 1,
          day: today.getDate(),
        };
      }
    }
    // パラメータがない場合は今日を使用
    const today = new Date();
    return {
      year: today.getFullYear(),
      month: today.getMonth() + 1,
      day: today.getDate(),
    };
  }, [searchParams]);

  const {
    selectedDate,
    selectedDateString,
    dayData,
    handleDateSelect,
    handleMonthChange,
    isLoading,
    isError,
    monthlyDataQuery,
  } = useCalendarModel({ initialDate });

  // 日付選択時にURLを更新
  useEffect(() => {
    const newDateString = formatCalendarDate(selectedDate);
    const currentDate = searchParams.get('date');

    if (currentDate !== newDateString) {
      const url = `/calendar?date=${newDateString}`;
      router.replace(url, { scroll: false });
    }
  }, [selectedDate, searchParams, router]);

  // 今日のページへ戻る
  const handleBackToToday = () => {
    router.push('/today');
  };

  // Todayページで表示するための日付文字列を取得
  const todayPageDate = selectedDateString;

  return (
    <div className="w-full space-y-6">
      {/* ページヘッダー */}
      <div className="flex items-center justify-between" data-tour="calendar-header">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <CalendarIcon className="w-6 h-6 text-blue-600" />
            <h1 className="text-2xl font-bold">カレンダー</h1>
            <TutorialTrigger tutorialId="feature_calendar" className="ml-auto" />
          </div>
          <p className="text-sm text-muted-foreground">
            日付を選択して食事記録を確認・編集できます
          </p>
        </div>

        <Button
          variant="outline"
          onClick={handleBackToToday}
          className="flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          今日に戻る
        </Button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* 左側: カレンダー */}
        <div className="space-y-4" data-tour="calendar-main">
          <Calendar
            selectedDate={selectedDate}
            onDateSelect={handleDateSelect}
            onMonthChange={handleMonthChange}
            dayData={dayData}
            className="w-full max-w-none"
          />

          {/* 選択日付の情報 */}
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800" data-tour="calendar-date-info">
            <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
              選択日: {selectedDate.year}年{selectedDate.month}月{selectedDate.day}日
            </h3>

            {/* ローディングとエラー状態 */}
            {isLoading && (
              <p className="text-sm text-blue-600 dark:text-blue-400 animate-pulse">
                データを読み込んでいます...
              </p>
            )}

            {isError && (
              <p className="text-sm text-red-600 dark:text-red-400">
                データの取得に失敗しました
              </p>
            )}

            {/* 選択日の概要情報 */}
            {!isLoading && !isError && (() => {
              const selectedDayData = dayData.find(d => d.date === selectedDateString);

              // データが見つからない場合（表示月と選択月が異なる場合など）
              if (!selectedDayData) {
                return (
                  <p className="text-sm text-blue-700 dark:text-blue-300">
                    この日のデータはまだありません
                  </p>
                );
              }

              // データがあるがすべて空の場合
              const hasAnyData = selectedDayData.hasMeals || selectedDayData.hasReport || selectedDayData.goalAchievementPercentage !== undefined;
              if (!hasAnyData) {
                return (
                  <p className="text-sm text-blue-600 dark:text-blue-400 italic">
                    まだデータが記録されていません
                  </p>
                );
              }

              // データがある場合の表示
              return (
                <div className="space-y-2 text-sm">
                  {selectedDayData.hasMeals && (
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-green-600 rounded-full"></span>
                      <span className="text-blue-700 dark:text-blue-300">
                        食事記録あり
                      </span>
                    </div>
                  )}

                  {selectedDayData.goalAchievementPercentage !== undefined && (
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${
                        selectedDayData.goalAchievementPercentage >= 80 ? 'bg-green-500' :
                        selectedDayData.goalAchievementPercentage >= 60 ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}></span>
                      <span className="text-blue-700 dark:text-blue-300">
                        目標達成度: {selectedDayData.goalAchievementPercentage}%
                      </span>
                    </div>
                  )}

                  {selectedDayData.hasReport && (
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-purple-600 rounded-full"></span>
                      <span className="text-blue-700 dark:text-blue-300">
                        AI レポート生成済み
                      </span>
                    </div>
                  )}

                  {!selectedDayData.hasMeals && (
                    <p className="text-blue-600 dark:text-blue-400 italic text-xs">
                      食事記録なし
                    </p>
                  )}
                </div>
              );
            })()}
          </div>
        </div>

        {/* 右側: 選択日の詳細（Todayページの内容を再利用） */}
        <div className="space-y-6" data-tour="calendar-detail-panel">
          <div className="border-l-4 border-blue-500 pl-4" data-tour="calendar-detail-header">
            <h2 className="text-lg font-semibold mb-1">
              {selectedDate.year}年{selectedDate.month}月{selectedDate.day}日の詳細
            </h2>
            <p className="text-sm text-muted-foreground">
              食事記録・栄養分析・目標達成度
            </p>
          </div>

          {/* TodayPageの内容をここに表示 */}
          <TodayPageContent date={todayPageDate} />
        </div>
      </div>
    </div>
  );
}