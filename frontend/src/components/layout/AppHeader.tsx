// frontend/components/layout/AppHeader.tsx
'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

type Plan = 'trial' | 'free' | 'paid';

type AppHeaderProps = {
  appName?: string;
  userName?: string;
  plan?: Plan;
  trialEndsAt?: string | null;
  onLogout?: () => void;
};

function renderPlanBadge(plan?: Plan, trialEndsAt?: string | null) {
  if (!plan) return null;
  if (plan === 'trial') {
    return (
      <Badge variant="warning">
        TRIAL
        {trialEndsAt && (
          <span className="ml-1 text-[10px] text-amber-300/80">
            ~ {trialEndsAt}
          </span>
        )}
      </Badge>
    );
  }
  if (plan === 'paid') {
    return <Badge variant="success">PAID</Badge>;
  }
  return <Badge variant="default">FREE</Badge>;
}

export function AppHeader({
  appName = 'Nutrition Lite',
  userName,
  plan,
  trialEndsAt,
  onLogout,
}: AppHeaderProps) {
  return (
    <header className="border-b border-slate-800 px-4 py-3 md:px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="h-8 w-8 rounded-xl bg-emerald-500/20 flex items-center justify-center">
          <span className="text-sm font-bold text-emerald-400">N</span>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-slate-50">
              {appName}
            </span>
            {renderPlanBadge(plan, trialEndsAt)}
          </div>
          <p className="text-xs text-slate-500">
            毎日の食事ログと栄養フィードバック
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {userName && (
          <div className="hidden md:flex flex-col items-end">
            <span className="text-sm text-slate-50">{userName}</span>
          </div>
        )}
        {onLogout && (
          <Button variant="ghost" size="sm" onClick={onLogout}>
            ログアウト
          </Button>
        )}
      </div>
    </header>
  );
}
