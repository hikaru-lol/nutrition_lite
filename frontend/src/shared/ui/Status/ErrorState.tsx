'use client';

import { Button } from '@/components/ui/button';

export function ErrorState(props: {
  title?: string;
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="w-full rounded-xl border p-6">
      <div className="text-base font-semibold">{props.title ?? 'Error'}</div>
      {props.message ? (
        <div className="mt-1 text-sm text-muted-foreground">
          {props.message}
        </div>
      ) : null}
      {props.onRetry ? (
        <Button variant="outline" className="mt-4" onClick={props.onRetry}>
          再試行
        </Button>
      ) : null}
    </div>
  );
}
