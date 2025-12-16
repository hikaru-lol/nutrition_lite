'use client';

import React from 'react';
import type { MealStatus, SortState } from '../../types';
import { Button } from '../../ui/Button';
import { Chip } from '../../ui/Chip';
import { cx } from '../../lib/cx';

export function SearchFilters({
  query,
  onQueryChange,
  statusFilter,
  onStatusFilterChange,
  sort,
  onSortChange,
  searchInputRef,
  onApply,
}: {
  query: string;
  onQueryChange: (v: string) => void;
  statusFilter: 'all' | MealStatus;
  onStatusFilterChange: (v: 'all' | MealStatus) => void;
  sort: SortState;
  onSortChange: (next: SortState) => void;
  searchInputRef: React.RefObject<HTMLInputElement>;
  onApply?: () => void;
}) {
  return (
    <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-950">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-1 items-center gap-3">
          <div className="relative flex-1">
            <input
              ref={searchInputRef}
              value={query}
              onChange={(e) => onQueryChange(e.target.value)}
              placeholder="Search by title or date... (press /)"
              className={cx(
                'w-full rounded-xl border px-4 py-2 text-sm outline-none transition',
                'border-gray-200 bg-white text-gray-900',
                'focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-white',
                'dark:border-gray-800 dark:bg-gray-950 dark:text-gray-100 dark:focus:ring-offset-gray-950'
              )}
            />
            <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
              /
            </div>
          </div>

          <Button variant="secondary" onClick={onApply}>
            Apply
          </Button>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Chip
            active={statusFilter === 'all'}
            onClick={() => onStatusFilterChange('all')}
          >
            All
          </Chip>
          <Chip
            active={statusFilter === 'logged'}
            onClick={() => onStatusFilterChange('logged')}
          >
            Logged
          </Chip>
          <Chip
            active={statusFilter === 'draft'}
            onClick={() => onStatusFilterChange('draft')}
          >
            Draft
          </Chip>
          <Chip
            active={statusFilter === 'flagged'}
            onClick={() => onStatusFilterChange('flagged')}
          >
            Flagged
          </Chip>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2 text-sm">
        <span className="text-gray-500 dark:text-gray-400">Sort:</span>
        {(
          [
            { key: 'date', label: 'Date' },
            { key: 'calories', label: 'Calories' },
            { key: 'protein', label: 'Protein' },
          ] as const
        ).map((s) => (
          <button
            key={s.key}
            className={cx(
              'rounded-lg px-3 py-1 transition',
              sort.key === s.key
                ? 'bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900'
                : 'text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-900'
            )}
            onClick={() =>
              onSortChange({
                key: s.key,
                dir:
                  sort.key === s.key
                    ? sort.dir === 'asc'
                      ? 'desc'
                      : 'asc'
                    : 'desc',
              })
            }
          >
            {s.label}{' '}
            {sort.key === s.key ? (sort.dir === 'asc' ? '↑' : '↓') : ''}
          </button>
        ))}
      </div>
    </section>
  );
}
