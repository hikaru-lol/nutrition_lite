// src/shared/ui/PageSkeleton.tsx
'use client';

import { Skeleton } from '@/components/ui/skeleton';

export function PageSkeleton(props: { title?: string; lines?: number }) {
  const lines = props.lines ?? 6;
  return (
    <div className="p-6 space-y-4">
      {props.title ? (
        <div className="text-xl font-semibold">{props.title}</div>
      ) : null}
      <div className="space-y-2 max-w-2xl">
        {Array.from({ length: lines }).map((_, i) => (
          <Skeleton key={i} className="h-4 w-full" />
        ))}
      </div>
    </div>
  );
}
