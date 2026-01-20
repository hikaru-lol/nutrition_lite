'use client';

import React from 'react';
import type { Totals } from '../../types';
import { Button } from '../../ui/Button';

export function Sidebar({
  totals,
  onOpenPalette,
  onNotify,
}: {
  totals: Totals;
  onOpenPalette: () => void;
  onNotify: (title: string, message?: string) => void;
}) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-3 px-4 py-4">
        <div className="grid h-10 w-10 place-items-center rounded-2xl bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900">
          N
        </div>
        <div className="min-w-0">
          <div className="truncate text-sm font-semibold">Nutrition UI</div>
          <div className="truncate text-xs text-gray-500 dark:text-gray-400">
            Recent + Sections
          </div>
        </div>
      </div>

      <div className="px-3">
        <div className="rounded-2xl border border-gray-200 bg-white p-3 shadow-sm dark:border-gray-800 dark:bg-gray-950">
          <div className="text-xs text-gray-500 dark:text-gray-400">Today</div>
          <div className="mt-1 text-sm font-semibold">{totals.day}</div>
          <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
            <div className="rounded-xl bg-gray-50 p-3 dark:bg-gray-900">
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Calories
              </div>
              <div className="mt-1 font-semibold">{totals.calories}</div>
            </div>
            <div className="rounded-xl bg-gray-50 p-3 dark:bg-gray-900">
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Protein
              </div>
              <div className="mt-1 font-semibold">{totals.protein}g</div>
            </div>
          </div>
        </div>
      </div>

      <nav className="mt-4 flex flex-1 flex-col gap-1 px-3">
        {[
          { label: 'Dashboard', icon: '▦', active: true },
          { label: 'Meals', icon: '🍽', active: false },
          { label: 'Targets', icon: '◎', active: false },
          { label: 'Billing', icon: '⎈', active: false },
          { label: 'Profile', icon: '👤', active: false },
          { label: 'Logout', icon: '🚪', active: false },
        ].map((it) => (
          <button
            key={it.label}
            type="button"
            className={
              it.active
                ? 'flex items-center gap-3 rounded-xl px-3 py-2 text-sm transition bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900'
                : 'flex items-center gap-3 rounded-xl px-3 py-2 text-sm transition text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-900'
            }
            onClick={() =>
              onNotify(`${it.label} navigation`, `${it.label} clicked`)
            }
          >
            <span className="w-6 text-center">{it.icon}</span>
            <span className="truncate">{it.label}</span>
          </button>
        ))}
      </nav>

      <div className="border-t border-gray-200 px-4 py-3 dark:border-gray-800">
        <Button variant="secondary" className="w-full" onClick={onOpenPalette}>
          Open Palette (⌘K)
        </Button>
      </div>
    </div>
  );
}
