'use client';

import React from 'react';
import { Button } from '../../ui/Button';

export function QuickActionsCard({
  onToast,
  onOpenPalette,
}: {
  onToast: (title: string, message?: string) => void;
  onOpenPalette: () => void;
}) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-950">
      <div className="text-sm font-semibold">Quick actions</div>
      <div className="mt-1 text-sm text-gray-600 dark:text-gray-400">
        パレットからも実行できます
      </div>

      <div className="mt-4 grid gap-2">
        <Button onClick={() => onToast('Logged', 'Marked as logged (demo)')}>
          Mark today as logged
        </Button>
        <Button
          variant="secondary"
          onClick={() => onToast('Sync', 'Sync started (demo)')}
        >
          Sync data
        </Button>
        <Button variant="secondary" onClick={onOpenPalette}>
          Open palette
        </Button>
      </div>
    </div>
  );
}
