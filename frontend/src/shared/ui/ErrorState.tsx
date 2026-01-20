// src/shared/ui/ErrorState.tsx
import React from 'react';

export function ErrorState(props: {
  title?: string;
  message: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="p-6">
      <div className="max-w-xl rounded-xl border p-6 space-y-3">
        <h2 className="text-lg font-semibold">
          {props.title ?? 'エラーが発生しました'}
        </h2>
        <p className="text-sm text-muted-foreground whitespace-pre-wrap">
          {props.message}
        </p>
        {props.action ? <div className="pt-2">{props.action}</div> : null}
      </div>
    </div>
  );
}
