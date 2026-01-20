// src/shared/ui/states/InlineSkeleton.tsx
'use client';

import { Skeleton } from '@/shared/ui/skeleton';

export function InlineSkeleton(props: { rows?: number }) {
  const rows = props.rows ?? 3;
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-5 w-full" />
      ))}
    </div>
  );
}
