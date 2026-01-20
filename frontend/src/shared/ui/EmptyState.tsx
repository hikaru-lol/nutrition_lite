// src/shared/ui/EmptyState.tsx
import React from 'react';

export function EmptyState(props: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="p-6">
      <div className="max-w-xl rounded-xl border p-6 space-y-3">
        <h2 className="text-lg font-semibold">{props.title}</h2>
        {props.description ? (
          <p className="text-sm text-muted-foreground">{props.description}</p>
        ) : null}
        {props.action ? <div className="pt-2">{props.action}</div> : null}
      </div>
    </div>
  );
}
