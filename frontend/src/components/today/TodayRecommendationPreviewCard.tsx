import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import type {
  Plan,
  TodayRecommendationPreview,
} from '@/lib/hooks/useTodayOverview';

type TodayRecommendationPreviewCardProps = {
  recommendation: TodayRecommendationPreview;
  plan: Plan;
  onNavigateToRecommendation: () => void;
  onNavigateToUpgrade: () => void;
};

export function TodayRecommendationPreviewCard({
  recommendation,
  plan,
  onNavigateToRecommendation,
  onNavigateToUpgrade,
}: TodayRecommendationPreviewCardProps) {
  const locked = plan === 'free';

  return (
    <Card>
      <div className="mb-2 flex items-center justify-between">
        <p className="text-xs text-slate-400">今日の提案</p>
      </div>

      {locked ? (
        <>
          <p className="text-xs text-slate-400 mb-3">
            提案機能は有料プランまたはトライアル中にご利用いただけます。
          </p>
          <Button
            size="sm"
            variant="secondary"
            className="w-full"
            onClick={onNavigateToUpgrade}
          >
            プランを確認する
          </Button>
        </>
      ) : recommendation.hasRecommendation ? (
        <>
          <p className="text-sm text-slate-100 line-clamp-3 mb-3">
            {recommendation.snippet}
          </p>
          <Button
            size="sm"
            variant="secondary"
            className="w-full"
            onClick={onNavigateToRecommendation}
          >
            提案を詳しく見る
          </Button>
        </>
      ) : (
        <>
          <p className="text-xs text-slate-400 mb-3">
            直近数日分のレポートが揃うと、ここに「次にどうすると良いか」の提案が表示されます。
          </p>
          <Button
            size="sm"
            variant="ghost"
            className="w-full"
            onClick={onNavigateToRecommendation}
          >
            提案画面を開く
          </Button>
        </>
      )}
    </Card>
  );
}
