'use client';

import React from 'react';
import type { Meal } from '../../types';
import { Button } from '../../ui/Button';
import { Skeleton } from '../../ui/Skeleton';
import { StatusPill } from './StatusPill';
import { formatNumber } from '../../lib/format';

export function MealsTable({
  loading,
  meals,
  onOpenDetails,
  onResetFilters,
}: {
  loading: boolean;
  meals: Meal[];
  onOpenDetails: (m: Meal) => void;
  onResetFilters: () => void;
}) {
  const shown = meals.slice(0, 10);

  return (
    <section className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm dark:border-gray-800 dark:bg-gray-950">
      <div className="flex items-center justify-between gap-3 border-b border-gray-200 px-5 py-4 dark:border-gray-800">
        <div>
          <div className="text-sm font-semibold">Meals</div>
          <div className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            {loading ? 'Loading…' : `${meals.length} items`}
          </div>
        </div>
        <Button variant="secondary" size="sm" onClick={onResetFilters}>
          Reset filters
        </Button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50 text-xs text-gray-500 dark:bg-gray-900 dark:text-gray-400">
            <tr>
              <th className="px-5 py-3 font-medium">Date</th>
              <th className="px-5 py-3 font-medium">Title</th>
              <th className="px-5 py-3 font-medium">Macros</th>
              <th className="px-5 py-3 font-medium">Status</th>
              <th className="px-5 py-3 font-medium"></th>
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
            {loading
              ? Array.from({ length: 6 }).map((_, i) => (
                  <tr key={i}>
                    <td className="px-5 py-4">
                      <Skeleton className="h-4 w-24" />
                    </td>
                    <td className="px-5 py-4">
                      <Skeleton className="h-4 w-44" />
                    </td>
                    <td className="px-5 py-4">
                      <Skeleton className="h-4 w-56" />
                    </td>
                    <td className="px-5 py-4">
                      <Skeleton className="h-5 w-20 rounded-full" />
                    </td>
                    <td className="px-5 py-4">
                      <Skeleton className="h-8 w-20" />
                    </td>
                  </tr>
                ))
              : shown.map((m) => (
                  <tr
                    key={m.id}
                    className="hover:bg-gray-50 dark:hover:bg-gray-900/60"
                  >
                    <td className="px-5 py-4 font-medium text-gray-900 dark:text-gray-100">
                      {m.date}
                    </td>
                    <td className="px-5 py-4">
                      <div className="font-medium text-gray-900 dark:text-gray-100">
                        {m.title}
                      </div>
                      <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                        {formatNumber(m.calories)} kcal
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex flex-wrap gap-2">
                        <span className="rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-700 dark:bg-gray-800 dark:text-gray-200">
                          P {formatNumber(m.protein)}g
                        </span>
                        <span className="rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-700 dark:bg-gray-800 dark:text-gray-200">
                          C {formatNumber(m.carbs)}g
                        </span>
                        <span className="rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-700 dark:bg-gray-800 dark:text-gray-200">
                          F {formatNumber(m.fat)}g
                        </span>
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <StatusPill status={m.status} />
                    </td>
                    <td className="px-5 py-4 text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onOpenDetails(m)}
                      >
                        Details →
                      </Button>
                    </td>
                  </tr>
                ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between border-t border-gray-200 px-5 py-4 text-sm dark:border-gray-800">
        <div className="text-gray-600 dark:text-gray-400">
          Showing 10 of {loading ? '—' : meals.length}
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" disabled>
            Prev
          </Button>
          <Button variant="secondary" size="sm">
            Next
          </Button>
        </div>
      </div>
    </section>
  );
}
