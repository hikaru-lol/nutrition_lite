// src/shared/ui/PageSkeleton.tsx
import React from 'react';

export function PageSkeleton(props: { title?: string; lines?: number }) {
  const lines = props.lines ?? 6;
  return (
    <div className="p-6 space-y-4">
      {props.title ? <div className="h-7 w-48 bg-muted rounded" /> : null}
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, i) => (
          <div key={i} className="h-4 bg-muted rounded" />
        ))}
      </div>
    </div>
  );
}
