'use client';

import { useState, useMemo, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { CalendarDate, CalendarDayData } from '@/shared/ui/calendar/Calendar';

// 日付関数ユーティリティ
function formatLocalDateYYYYMMDD(d: Date): string {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

function parseCalendarDate(dateString: string): CalendarDate {
  const [year, month, day] = dateString.split('-').map(Number);
  return { year, month, day };
}

function calendarDateToString(date: CalendarDate): string {
  return `${date.year}-${String(date.month).padStart(2, '0')}-${String(date.day).padStart(2, '0')}`;
}

function getTodayCalendarDate(): CalendarDate {
  const today = new Date();
  return {
    year: today.getFullYear(),
    month: today.getMonth() + 1,
    day: today.getDate(),
  };
}

interface UseCalendarModelProps {
  initialDate?: CalendarDate;
}

export function useCalendarModel({
  initialDate = getTodayCalendarDate()
}: UseCalendarModelProps = {}) {

  // 選択された日付
  const [selectedDate, setSelectedDate] = useState<CalendarDate>(initialDate);

  // 現在表示中の年月（カレンダーナビゲーション用）
  const [viewingYear, setViewingYear] = useState(initialDate.year);
  const [viewingMonth, setViewingMonth] = useState(initialDate.month);

  // 今日の日付
  const today = useMemo(() => getTodayCalendarDate(), []);

  // 選択日付の文字列形式
  const selectedDateString = useMemo(() =>
    calendarDateToString(selectedDate),
    [selectedDate]
  );

  // TODO: Phase 3で月次データ取得API統合
  // 現在はダミーデータを返すクエリ
  const monthlyDataQuery = useQuery({
    queryKey: ['calendar', 'monthly', viewingYear, viewingMonth],
    queryFn: async (): Promise<CalendarDayData[]> => {
      // Phase 3で実装予定の月次データ取得
      // const response = await fetchMonthlyCalendarData(viewingYear, viewingMonth);
      // return response;

      // 暫定的にダミーデータを返す
      const daysInMonth = new Date(viewingYear, viewingMonth, 0).getDate();
      const dummyData: CalendarDayData[] = [];

      for (let day = 1; day <= daysInMonth; day++) {
        const dateStr = `${viewingYear}-${String(viewingMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const isToday = dateStr === formatLocalDateYYYYMMDD(new Date());

        // ランダムにデータを生成（デモ用）
        const hasMeals = Math.random() > 0.3; // 70%の確率で食事記録あり
        const goalAchievementPercentage = hasMeals ? Math.floor(Math.random() * 100) : undefined;
        const hasReport = hasMeals && Math.random() > 0.5;

        dummyData.push({
          date: dateStr,
          hasMeals,
          mealCount: hasMeals ? Math.floor(Math.random() * 5) + 1 : 0,
          goalAchievementPercentage,
          hasReport,
          isToday,
          isSelected: dateStr === selectedDateString,
        });
      }

      return dummyData;
    },
    staleTime: 5 * 60 * 1000, // 5分間キャッシュ
  });

  // 日付選択ハンドラ
  const handleDateSelect = useCallback((date: CalendarDate) => {
    setSelectedDate(date);
  }, []);

  // 月変更ハンドラ
  const handleMonthChange = useCallback((year: number, month: number) => {
    setViewingYear(year);
    setViewingMonth(month);
  }, []);

  // 今日に戻る
  const goToToday = useCallback(() => {
    const todayDate = getTodayCalendarDate();
    setSelectedDate(todayDate);
    setViewingYear(todayDate.year);
    setViewingMonth(todayDate.month);
  }, []);

  // 特定の日付に移動
  const goToDate = useCallback((dateString: string) => {
    const date = parseCalendarDate(dateString);
    setSelectedDate(date);
    setViewingYear(date.year);
    setViewingMonth(date.month);
  }, []);

  // 前月・次月ナビゲーション
  const goToPrevMonth = useCallback(() => {
    const prevMonth = viewingMonth === 1 ? 12 : viewingMonth - 1;
    const prevYear = viewingMonth === 1 ? viewingYear - 1 : viewingYear;
    handleMonthChange(prevYear, prevMonth);
  }, [viewingYear, viewingMonth, handleMonthChange]);

  const goToNextMonth = useCallback(() => {
    const nextMonth = viewingMonth === 12 ? 1 : viewingMonth + 1;
    const nextYear = viewingMonth === 12 ? viewingYear + 1 : viewingYear;
    handleMonthChange(nextYear, nextMonth);
  }, [viewingYear, viewingMonth, handleMonthChange]);

  // 選択日が今日かどうか
  const isSelectedToday = useMemo(() => {
    return selectedDateString === formatLocalDateYYYYMMDD(new Date());
  }, [selectedDateString]);

  // 月次データ（UIに渡すデータ）
  const dayData = monthlyDataQuery.data || [];

  return {
    // 選択状態
    selectedDate,
    selectedDateString,
    viewingYear,
    viewingMonth,
    today,
    isSelectedToday,

    // データ
    dayData,
    monthlyDataQuery,

    // アクション
    handleDateSelect,
    handleMonthChange,
    goToToday,
    goToDate,
    goToPrevMonth,
    goToNextMonth,

    // 状態フラグ
    isLoading: monthlyDataQuery.isLoading,
    isError: monthlyDataQuery.isError,
  };
}