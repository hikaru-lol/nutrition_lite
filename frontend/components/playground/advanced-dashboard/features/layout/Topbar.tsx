'use client';

import React from 'react';
import { IconButton } from '../../ui/IconButton';
import { Button } from '../../ui/Button';

export function Topbar({
  onOpenSidebar,
  onOpenPalette,
}: {
  onOpenSidebar: () => void;
  onOpenPalette: () => void;
}) {
  return (
    <header className="sticky top-0 z-20 border-b border-gray-200 bg-white/80 backdrop-blur dark:border-gray-800 dark:bg-gray-950/60">
      <div className="mx-auto flex max-w-5xl items-center gap-3 px-4 py-3">
        <IconButton
          label="Open sidebar"
          className="lg:hidden"
          onClick={onOpenSidebar}
        >
          ☰
        </IconButton>

        <div className="min-w-0 flex-1">
          <div className="text-sm font-semibold">Meals Dashboard</div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            ⌘K: palette • /: focus search
          </div>
        </div>

        <Button variant="secondary" size="sm" onClick={onOpenPalette}>
          ⌘K
        </Button>
      </div>
    </header>
  );
}
