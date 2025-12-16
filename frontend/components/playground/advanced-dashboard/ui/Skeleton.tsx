'use client';

import React from 'react';
import { cx } from '../lib/cx';

export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cx(
        'animate-pulse rounded-lg bg-gray-200 dark:bg-gray-800',
        className
      )}
    />
  );
}
