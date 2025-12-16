'use client';

import { useEffect } from 'react';
import { isTypingTarget } from '../lib/dom';

export function useGlobalHotkeys(args: {
  onOpenPalette: () => void;
  onFocusSearch: () => void;
}) {
  const { onOpenPalette, onFocusSearch } = args;

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      const isK = e.key.toLowerCase() === 'k';
      if (isK && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        onOpenPalette();
        return;
      }

      if (e.key === '/' && !e.metaKey && !e.ctrlKey && !e.altKey) {
        const activeEl = document.activeElement as Element | null;
        if (isTypingTarget(activeEl)) return;
        e.preventDefault();
        onFocusSearch();
      }
    };

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [onOpenPalette, onFocusSearch]);
}
