// src/shared/ui/states/PageSkeleton.tsx
'use client';

import { Skeleton } from '@/shared/ui/skeleton';

export function PageSkeleton(props: { lines?: number }) {
  const lines = props.lines ?? 8;
  return (
    <div className="space-y-3">
      <Skeleton className="h-8 w-1/3" />
      <Skeleton className="h-4 w-2/3" />
      <div className="pt-2 space-y-2">
        {Array.from({ length: lines }).map((_, i) => (
          <Skeleton key={i} className="h-10 w-full" />
        ))}
      </div>
    </div>
  );
}
