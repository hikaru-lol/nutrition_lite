'use client';

import React from 'react';
import type { MealStatus } from '../../types';
import { cx } from '../../lib/cx';

export function StatusPill({ status }: { status: MealStatus }) {
  const map: Record<MealStatus, { label: string; cls: string }> = {
    logged: {
      label: 'Logged',
      cls: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-200',
    },
    draft: {
      label: 'Draft',
      cls: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100',
    },
    flagged: {
      label: 'Flagged',
      cls: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-200',
    },
  };
  const s = map[status];
  return (
    <span
      className={cx(
        'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium',
        s.cls
      )}
    >
      {s.label}
    </span>
  );
}
