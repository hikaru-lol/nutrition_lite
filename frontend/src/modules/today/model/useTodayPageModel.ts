'use client';

import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { fetchTodaySummary } from '../api/todayClient';
import { DateISOSchema } from '../contract/todayContract';

function todayISO(): string {
  // クライアントのローカル日付でOK（ユーザーが日本前提）
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

export type TodayPageState = { type: 'idle' } | { type: 'ready' };

export function useTodayPageModel() {
  const [selectedDate, setSelectedDate] = useState<string>(todayISO());

  // UI側で date input を使うので、ここで最低限の検証だけしておく
  const safeDate = useMemo(() => {
    const r = DateISOSchema.safeParse(selectedDate);
    return r.success ? r.data : todayISO();
  }, [selectedDate]);

  const todayQuery = useQuery({
    queryKey: ['today', safeDate],
    queryFn: () => fetchTodaySummary(safeDate),
  });

  const state: TodayPageState = { type: 'ready' };

  const hasActiveTarget = !!todayQuery.data?.active_target;
  const meals = todayQuery.data?.meals ?? [];

  return {
    // state
    state,
    selectedDate,
    setSelectedDate,
    safeDate,

    // query
    todayQuery,

    // derived
    hasActiveTarget,
    meals,
  };
}
