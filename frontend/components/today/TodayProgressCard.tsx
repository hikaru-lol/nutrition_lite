import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type { TodayProgress } from '@/lib/hooks/useTodayOverview';

type TodayProgressCardProps = {
  progress: TodayProgress;
  onNavigateToMeals: () => void;
  onNavigateToReport: () => void;
};

export function TodayProgressCard({
  progress,
  onNavigateToMeals,
  onNavigateToReport,
}: TodayProgressCardProps) {
  const { mealsPerDay, filledCount, isCompleted } = progress;
  const ratio = mealsPerDay > 0 ? filledCount / mealsPerDay : 0;
  const percentage = Math.min(100, Math.round(ratio * 100));

  return (
    <Card>
      <div className="flex items-center justify-between mb-3">
        <div>
          <p className="text-xs text-slate-400">今日の記録</p>
          <p className="mt-1 text-lg font-semibold text-slate-50">
            {filledCount} / {mealsPerDay} 食
          </p>
        </div>
        {isCompleted && (
          <span className="text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/40 rounded-full px-2 py-0.5">
            記録完了 🎉
          </span>
        )}
      </div>

      <div className="mb-3">
        <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
          <div
            className="h-full rounded-full bg-emerald-500 transition-all"
            style={{ width: `${percentage}%` }}
          />
        </div>
        <p className="mt-1 text-xs text-slate-400">
          {isCompleted
            ? '今日の分はすべて記録できています。'
            : 'あと少しで記録完了です。'}
        </p>
      </div>

      <div className="flex gap-2">
        <Button
          variant="secondary"
          size="sm"
          className="flex-1"
          onClick={onNavigateToMeals}
        >
          食事を記録する
        </Button>
        <Button
          variant="primary"
          size="sm"
          className="flex-1"
          onClick={onNavigateToReport}
          disabled={!isCompleted}
        >
          レポートを見る
        </Button>
      </div>
    </Card>
  );
}
