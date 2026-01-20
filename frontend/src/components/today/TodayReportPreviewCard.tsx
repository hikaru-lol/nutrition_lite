import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type { Plan, TodayReportPreview } from '@/lib/hooks/useTodayOverview';

type TodayReportPreviewCardProps = {
  report: TodayReportPreview;
  isCompleted: boolean;
  plan: Plan;
  onNavigateToReport: () => void;
  onNavigateToUpgrade: () => void;
};

export function TodayReportPreviewCard({
  report,
  isCompleted,
  plan,
  onNavigateToReport,
  onNavigateToUpgrade,
}: TodayReportPreviewCardProps) {
  const locked = plan === 'free';

  return (
    <Card>
      <div className="mb-2 flex items-center justify-between">
        <p className="text-xs text-slate-400">日次レポート</p>
      </div>

      {locked ? (
        <>
          <p className="text-xs text-slate-400 mb-3">
            日次レポートは有料プランまたはトライアル中にご利用いただけます。
          </p>
          <Button size="sm" className="w-full" onClick={onNavigateToUpgrade}>
            プランを確認する
          </Button>
        </>
      ) : report.hasReport ? (
        <>
          <p className="text-sm text-slate-100 line-clamp-3 mb-3">
            {report.summary}
          </p>
          <Button
            variant="secondary"
            size="sm"
            className="w-full"
            onClick={onNavigateToReport}
          >
            レポートを開く
          </Button>
        </>
      ) : (
        <>
          <p className="text-xs text-slate-400 mb-3">
            まだ今日のレポートは生成されていません。
            {isCompleted
              ? ' ボタンを押して振り返りを作成できます。'
              : ' まずは今日の食事をすべて記録しましょう。'}
          </p>
          <Button
            size="sm"
            className="w-full"
            onClick={onNavigateToReport}
            disabled={!isCompleted}
          >
            レポートを作成する
          </Button>
        </>
      )}
    </Card>
  );
}
