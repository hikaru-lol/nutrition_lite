import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type { TodayMealsSummary } from '@/lib/hooks/useTodayOverview';

type TodayMealsSummaryCardProps = {
  mealsSummary: TodayMealsSummary;
  onNavigateToMeals: () => void;
};

export function TodayMealsSummaryCard({
  mealsSummary,
  onNavigateToMeals,
}: TodayMealsSummaryCardProps) {
  const { mainMeals, snackCount } = mealsSummary;

  return (
    <Card>
      <div className="mb-3 flex items-center justify-between">
        <div>
          <p className="text-xs text-slate-400">今日の食事サマリ</p>
          <p className="mt-1 text-sm text-slate-200">
            メイン {mainMeals.reduce((acc, m) => acc + m.itemCount, 0)} 品 /
            間食 {snackCount} 品
          </p>
        </div>
      </div>

      <div className="space-y-2 mb-3">
        {mainMeals.map((m) => (
          <div
            key={m.mealIndex}
            className="flex items-center justify-between text-xs"
          >
            <span className="text-slate-400">{m.mealIndex} 回目の食事</span>
            <span className="text-slate-100">{m.itemCount} 品</span>
          </div>
        ))}
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">間食</span>
          <span className="text-slate-100">{snackCount} 品</span>
        </div>
      </div>

      <Button
        variant="secondary"
        size="sm"
        className="w-full"
        onClick={onNavigateToMeals}
      >
        詳細を開く
      </Button>
    </Card>
  );
}
