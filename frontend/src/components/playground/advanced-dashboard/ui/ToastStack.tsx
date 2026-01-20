'use client';

import React from 'react';
import type { Toast } from '../types';

export function ToastStack({
  toasts,
  dismiss,
}: {
  toasts: Toast[];
  dismiss: (id: string) => void;
}) {
  return (
    <div className="fixed bottom-4 right-4 z-50 flex w-[min(92vw,360px)] flex-col gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className="rounded-2xl border border-gray-200 bg-white p-4 shadow-lg dark:border-gray-800 dark:bg-gray-950"
        >
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <div className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                {t.title}
              </div>
              {t.message && (
                <div className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                  {t.message}
                </div>
              )}
            </div>
            <button
              className="rounded-lg px-2 py-1 text-sm text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-900"
              onClick={() => dismiss(t.id)}
            >
              Close
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
