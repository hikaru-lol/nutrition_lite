'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function BillingPlanPage() {
  return (
    <div className="mx-auto w-full max-w-3xl p-6">
      <Card>
        <CardHeader>
          <CardTitle>料金プラン</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-muted-foreground">
            料金プラン機能は準備中です。
          </div>
        </CardContent>
      </Card>
    </div>
  );
}