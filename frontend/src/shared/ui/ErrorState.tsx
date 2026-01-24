// src/shared/ui/ErrorState.tsx
'use client';

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export function ErrorState(props: {
  title?: string;
  message: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="p-6">
      <div className="max-w-xl space-y-3">
        <Alert>
          <AlertTitle>{props.title ?? 'エラーが発生しました'}</AlertTitle>
          <AlertDescription className="whitespace-pre-wrap">
            {props.message}
          </AlertDescription>
        </Alert>
        {props.action ? <div>{props.action}</div> : null}
      </div>
    </div>
  );
}
