'use client';

import React from 'react';
import type { Totals } from '../../types';
import { formatNumber } from '../../lib/format';
import { Skeleton } from '../../ui/Skeleton';
import { MiniLineChart } from '../../charts/MiniLineChart';

export function KpiPanel({
  loading,
  totals,
  weekCalories,
}: {
  loading: boolean;
  totals: Totals;
  weekCalories: number[];
}) {
  const avg = Math.round(
    weekCalories.reduce((a, b) => a + b, 0) / Math.max(1, weekCalories.length)
  );

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-950">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-sm font-semibold">This week calories</div>
          <div className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Recent & Sections
          </div>
        </div>
        <div className="rounded-xl bg-blue-50 px-3 py-2 text-sm font-semibold text-blue-700 dark:bg-blue-900/30 dark:text-blue-200">
          Avg {formatNumber(avg)}
        </div>
      </div>

      <div className="mt-4 flex items-end justify-between gap-4">
        <div className="text-3xl font-semibold">
          {loading
            ? '—'
            : formatNumber(weekCalories[weekCalories.length - 1] ?? 0)}
        </div>
        <div className="text-blue-600">
          {loading ? (
            <Skeleton className="h-14 w-60" />
          ) : (
            <MiniLineChart points={weekCalories} />
          )}
        </div>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-4">
        {[
          { label: 'Calories', value: `${formatNumber(totals.calories)}` },
          { label: 'Protein', value: `${formatNumber(totals.protein)}g` },
          { label: 'Carbs', value: `${formatNumber(totals.carbs)}g` },
          { label: 'Fat', value: `${formatNumber(totals.fat)}g` },
        ].map((it) => (
          <div
            key={it.label}
            className="rounded-2xl bg-gray-50 p-4 dark:bg-gray-900"
          >
            <div className="text-xs text-gray-500 dark:text-gray-400">
              {it.label}
            </div>
            <div className="mt-1 text-sm font-semibold">
              {loading ? <Skeleton className="h-4 w-16" /> : it.value}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
