'use client';

import React from 'react';

export function KbdCombo({ label }: { label: string }) {
  return (
    <span className="inline-flex items-center gap-1">
      {label.split('+').map((k, idx) => (
        <kbd
          key={`${k}-${idx}`}
          className="rounded-md border border-gray-200 bg-white px-1.5 py-0.5 text-[10px] font-medium text-gray-600 shadow-sm dark:border-gray-800 dark:bg-gray-950 dark:text-gray-300"
        >
          {k}
        </kbd>
      ))}
    </span>
  );
}
