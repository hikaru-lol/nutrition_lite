'use client';

import { useState } from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

import { CalendarHeader } from './CalendarHeader';
import { CalendarCell } from './CalendarCell';

export interface CalendarDate {
  year: number;
  month: number; // 1-12
  day: number;
}

export interface CalendarDayData {
  date: string; // YYYY-MM-DD
  hasMeals: boolean;
  mealCount?: number;
  goalAchievementPercentage?: number;
  hasReport?: boolean;
  isToday?: boolean;
  isSelected?: boolean;
}

interface CalendarProps {
  selectedDate: CalendarDate;
  onDateSelect: (date: CalendarDate) => void;
  onMonthChange: (year: number, month: number) => void;
  dayData?: CalendarDayData[];
  className?: string;
}

export function Calendar({
  selectedDate,
  onDateSelect,
  onMonthChange,
  dayData = [],
  className = '',
}: CalendarProps) {
  const today = new Date();
  const currentYear = selectedDate.year;
  const currentMonth = selectedDate.month;

  // 月の日数を取得
  const getDaysInMonth = (year: number, month: number): number => {
    return new Date(year, month, 0).getDate();
  };

  // 月の最初の曜日を取得 (0=日曜日)
  const getFirstDayOfMonth = (year: number, month: number): number => {
    return new Date(year, month - 1, 1).getDay();
  };

  // 前月の最後の日を取得
  const getLastDayOfPrevMonth = (year: number, month: number): number => {
    return new Date(year, month - 1, 0).getDate();
  };

  // カレンダーグリッドのデータを生成
  const generateCalendarGrid = () => {
    const daysInMonth = getDaysInMonth(currentYear, currentMonth);
    const firstDayOfWeek = getFirstDayOfMonth(currentYear, currentMonth);
    const daysInPrevMonth = getLastDayOfPrevMonth(currentYear, currentMonth);

    const calendarDays: (CalendarDate & { isCurrentMonth: boolean; dayData?: CalendarDayData })[] = [];

    // 前月の日付（グレーアウト）
    for (let i = firstDayOfWeek - 1; i >= 0; i--) {
      const day = daysInPrevMonth - i;
      const prevMonth = currentMonth === 1 ? 12 : currentMonth - 1;
      const prevYear = currentMonth === 1 ? currentYear - 1 : currentYear;

      calendarDays.push({
        year: prevYear,
        month: prevMonth,
        day,
        isCurrentMonth: false,
      });
    }

    // 現在月の日付
    for (let day = 1; day <= daysInMonth; day++) {
      const dateString = formatDateString(currentYear, currentMonth, day);
      const data = dayData.find(d => d.date === dateString);

      // デバッグ用ログ（開発時のみ）
      if (process.env.NODE_ENV === 'development' && day <= 3) {
        console.log(`Calendar debug: ${dateString}`, {
          found: !!data,
          data,
          dayDataLength: dayData.length,
          firstDayData: dayData[0]
        });
      }

      calendarDays.push({
        year: currentYear,
        month: currentMonth,
        day,
        isCurrentMonth: true,
        dayData: data,
      });
    }

    // 来月の日付（グリッドを6週間分埋めるため）
    const remainingCells = 42 - calendarDays.length; // 7×6グリッド
    for (let day = 1; day <= remainingCells; day++) {
      const nextMonth = currentMonth === 12 ? 1 : currentMonth + 1;
      const nextYear = currentMonth === 12 ? currentYear + 1 : currentYear;

      calendarDays.push({
        year: nextYear,
        month: nextMonth,
        day,
        isCurrentMonth: false,
      });
    }

    return calendarDays;
  };

  // YYYY-MM-DD フォーマット
  const formatDateString = (year: number, month: number, day: number): string => {
    return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  };

  // 今日かどうかを判定
  const isToday = (date: CalendarDate): boolean => {
    return (
      date.year === today.getFullYear() &&
      date.month === today.getMonth() + 1 &&
      date.day === today.getDate()
    );
  };

  // 選択された日付かどうかを判定
  const isSelected = (date: CalendarDate): boolean => {
    return (
      date.year === selectedDate.year &&
      date.month === selectedDate.month &&
      date.day === selectedDate.day
    );
  };

  // 日付選択ハンドラ
  const handleDateClick = (date: CalendarDate & { isCurrentMonth: boolean }) => {
    if (!date.isCurrentMonth) {
      // 異なる月の日付がクリックされた場合、その月に移動
      onMonthChange(date.year, date.month);
    }
    onDateSelect({
      year: date.year,
      month: date.month,
      day: date.day,
    });
  };

  // 前月・次月ナビゲーション
  const handlePrevMonth = () => {
    const prevMonth = currentMonth === 1 ? 12 : currentMonth - 1;
    const prevYear = currentMonth === 1 ? currentYear - 1 : currentYear;
    onMonthChange(prevYear, prevMonth);
  };

  const handleNextMonth = () => {
    const nextMonth = currentMonth === 12 ? 1 : currentMonth + 1;
    const nextYear = currentMonth === 12 ? currentYear + 1 : currentYear;
    onMonthChange(nextYear, nextMonth);
  };

  // 今日に戻る
  const handleTodayClick = () => {
    const todayDate = {
      year: today.getFullYear(),
      month: today.getMonth() + 1,
      day: today.getDate(),
    };
    onMonthChange(todayDate.year, todayDate.month);
    onDateSelect(todayDate);
  };

  const calendarGrid = generateCalendarGrid();
  const weekdays = ['日', '月', '火', '水', '木', '金', '土'];

  return (
    <Card className={`w-full max-w-md mx-auto ${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <CalendarIcon className="w-5 h-5" />
            カレンダー
          </CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={handleTodayClick}
            className="text-xs"
          >
            今日
          </Button>
        </div>

        <CalendarHeader
          year={currentYear}
          month={currentMonth}
          onPrevMonth={handlePrevMonth}
          onNextMonth={handleNextMonth}
        />
      </CardHeader>

      <CardContent className="p-4 pt-0">
        {/* 曜日ヘッダー */}
        <div className="grid grid-cols-7 gap-1 mb-2">
          {weekdays.map((day, index) => (
            <div
              key={day}
              className={`text-center text-sm font-medium py-2 ${
                index === 0 ? 'text-red-600' : index === 6 ? 'text-blue-600' : 'text-gray-600'
              }`}
            >
              {day}
            </div>
          ))}
        </div>

        {/* カレンダーグリッド */}
        <div className="grid grid-cols-7 gap-1">
          {calendarGrid.map((date, index) => (
            <CalendarCell
              key={`${date.year}-${date.month}-${date.day}`}
              date={date}
              isCurrentMonth={date.isCurrentMonth}
              isToday={isToday(date)}
              isSelected={isSelected(date)}
              dayData={date.dayData}
              onClick={() => handleDateClick(date)}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}