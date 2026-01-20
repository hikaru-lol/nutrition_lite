// src/shared/ui/states/ErrorState.tsx
'use client';

import { ApiError } from '@/shared/lib/api/fetcher';
import { Alert, AlertDescription, AlertTitle } from '@/shared/ui/alert';
import { Button } from '@/shared/ui/button';

function toMessage(error: unknown): { title: string; description?: string } {
  if (error instanceof ApiError) {
    return {
      title: `エラー (${error.status}${error.code ? ` / ${error.code}` : ''})`,
      description: error.message,
    };
  }
  if (error instanceof Error) {
    return { title: 'エラー', description: error.message };
  }
  return { title: 'エラー', description: '不明なエラーが発生しました' };
}

export function ErrorState(props: {
  error: unknown;
  title?: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
  const msg = toMessage(props.error);
  return (
    <Alert>
      <AlertTitle>{props.title ?? msg.title}</AlertTitle>
      {msg.description ? (
        <AlertDescription className="mt-1">{msg.description}</AlertDescription>
      ) : null}

      {props.onAction ? (
        <div className="mt-4">
          <Button variant="secondary" onClick={props.onAction}>
            {props.actionLabel ?? '再試行'}
          </Button>
        </div>
      ) : null}
    </Alert>
  );
}
