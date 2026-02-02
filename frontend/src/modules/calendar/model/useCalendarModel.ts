'use client';

import { useState, useMemo, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { CalendarDate } from '@/shared/ui/calendar/Calendar';
import { fetchMonthlyCalendar } from '../api/calendarClient';
import { toCalendarDayData } from '../contract/calendarContract';

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

  // 月次データ取得API
  const monthlyDataQuery = useQuery({
    queryKey: ['calendar', 'monthly', viewingYear, viewingMonth],
    queryFn: () => fetchMonthlyCalendar(viewingYear, viewingMonth),
    staleTime: 5 * 60 * 1000, // 5分間キャッシュ
  });

  // 日付選択ハンドラ
  const handleDateSelect = useCallback((date: CalendarDate) => {
    setSelectedDate(date);
    // 異なる月の日付が選択された場合、表示月も更新
    if (date.year !== viewingYear || date.month !== viewingMonth) {
      setViewingYear(date.year);
      setViewingMonth(date.month);
    }
  }, [viewingYear, viewingMonth]);

  // 月変更ハンドラ
  const handleMonthChange = useCallback((year: number, month: number) => {
    setViewingYear(year);
    setViewingMonth(month);
    // 選択日もその月の1日に更新
    setSelectedDate({ year, month, day: 1 });
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

  // バックエンドデータをUI用データに変換
  const dayData = useMemo(() => {
    if (!monthlyDataQuery.data) {
      console.log('Calendar Model: No data from API');
      return [];
    }

    const converted = monthlyDataQuery.data.days.map(snapshot =>
      toCalendarDayData(
        snapshot,
        snapshot.date === formatLocalDateYYYYMMDD(new Date()), // isToday
        snapshot.date === selectedDateString // isSelected
      )
    );

    // デバッグ用ログ（開発時のみ、有効なデータがある場合のみ）
    if (process.env.NODE_ENV === 'development') {
      const itemsWithData = converted.filter(d => d.hasMeals || d.hasReport || d.goalAchievementPercentage !== undefined);
      if (itemsWithData.length > 0) {
        console.log('Calendar Model: Data with content found', {
          month: `${viewingYear}-${viewingMonth}`,
          totalDays: converted.length,
          daysWithData: itemsWithData.length,
          sampleData: itemsWithData[0]
        });
      }
    }

    return converted;
  }, [monthlyDataQuery.data, selectedDateString, viewingYear, viewingMonth]);

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