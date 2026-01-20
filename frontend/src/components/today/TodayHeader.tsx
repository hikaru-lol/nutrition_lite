import type { Plan } from '@/lib/hooks/useTodayOverview';
import { Badge } from '@/components/ui/badge';

type TodayHeaderProps = {
  userName: string;
  plan: Plan;
  trialEndsAt?: string | null;
};

export function TodayHeader({ userName, plan, trialEndsAt }: TodayHeaderProps) {
  const planLabel =
    plan === 'trial' ? 'TRIAL' : plan === 'paid' ? 'PAID' : 'FREE';

  return (
    <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
      <div>
        <p className="text-lg font-semibold text-slate-400">
          今日のコンディション
        </p>
        <h1 className="mt-1 text-xl md:text-2xl font-semibold text-slate-50">
          おかえりなさい、{userName} さん
        </h1>
      </div>
      <div className="flex items-center gap-3">
        <Badge
          variant={
            plan === 'trial'
              ? 'warning'
              : plan === 'paid'
              ? 'success'
              : 'default'
          }
        >
          {planLabel}
        </Badge>
        {plan === 'trial' && trialEndsAt && (
          <span className="text-xs text-amber-300/80">
            トライアル終了予定日: {trialEndsAt}
          </span>
        )}
      </div>
    </div>
  );
}
