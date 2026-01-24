// src/shared/ui/EmptyState.tsx
'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function EmptyState(props: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="p-6">
      <Card className="max-w-xl">
        <CardHeader>
          <CardTitle className="text-lg">{props.title}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {props.description ? (
            <p className="text-sm text-muted-foreground">{props.description}</p>
          ) : null}
          {props.action ? <div>{props.action}</div> : null}
        </CardContent>
      </Card>
    </div>
  );
}
