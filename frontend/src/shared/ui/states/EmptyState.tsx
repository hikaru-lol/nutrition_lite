// src/shared/ui/states/EmptyState.tsx
'use client';

import { Button } from '@/shared/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card';

export function EmptyState(props: {
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{props.title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {props.description ? (
          <p className="text-sm text-muted-foreground">{props.description}</p>
        ) : null}
        {props.onAction ? (
          <Button onClick={props.onAction}>
            {props.actionLabel ?? '作成する'}
          </Button>
        ) : null}
      </CardContent>
    </Card>
  );
}
