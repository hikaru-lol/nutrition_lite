import type { Plan } from '@/lib/hooks/useTodayOverview';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

type UpgradeBannerProps = {
  plan: Plan;
  trialEndsAt?: string | null;
  onUpgradeClick: () => void;
};

export function UpgradeBanner({
  plan,
  trialEndsAt,
  onUpgradeClick,
}: UpgradeBannerProps) {
  if (plan === 'paid') return null;

  return (
    <Card className="border-amber-500/40 bg-amber-500/5">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs text-amber-400 font-semibold">
            {plan === 'trial' ? 'トライアル中' : 'FREE プラン'}
          </p>
          <p className="mt-1 text-sm text-slate-100">
            {plan === 'trial'
              ? trialEndsAt
                ? `トライアルは ${trialEndsAt} までご利用いただけます。有料プランにアップグレードすると、提案機能などを継続してお使いいただけます。`
                : 'トライアル期間中は、有料プランと同じ機能をお試しいただけます。'
              : '有料プランにアップグレードすると、日次レポートや提案機能をフルに活用できます。'}
          </p>
        </div>
        <Button size="sm" onClick={onUpgradeClick}>
          プランを確認する
        </Button>
      </div>
    </Card>
  );
}
