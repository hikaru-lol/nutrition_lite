'use client';

import { useEffect, useRef, useState } from 'react';
import type { Toast } from '../types';

export function useToasts(opts?: { max?: number; durationMs?: number }) {
  const max = opts?.max ?? 3;
  const durationMs = opts?.durationMs ?? 2600;

  const [toasts, setToasts] = useState<Toast[]>([]);
  const timers = useRef<Record<string, number>>({});

  const dismissToast = (id: string) => {
    setToasts((ts) => ts.filter((t) => t.id !== id));
    const handle = timers.current[id];
    if (handle) window.clearTimeout(handle);
    delete timers.current[id];
  };

  const pushToast = (title: string, message?: string) => {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    setToasts((ts) => [{ id, title, message }, ...ts].slice(0, max));

    timers.current[id] = window.setTimeout(() => dismissToast(id), durationMs);
  };

  useEffect(() => {
    return () => {
      Object.values(timers.current).forEach((h) => window.clearTimeout(h));
      timers.current = {};
    };
  }, []);

  return { toasts, pushToast, dismissToast };
}
