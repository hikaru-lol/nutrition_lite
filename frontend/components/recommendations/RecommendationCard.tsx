// frontend/components/recommendations/RecommendationCard.tsx
import { Card } from '@/components/ui/card';
import type { TodayRecommendationVM } from '@/lib/hooks/useTodayRecommendation';

type RecommendationCardProps = {
  recommendation: TodayRecommendationVM;
};

export function RecommendationCard({
  recommendation,
}: RecommendationCardProps) {
  const { date, body, tips } = recommendation;

  return (
    <Card>
      <div className="mb-2">
        <p className="text-xs text-slate-400">対象日: {date}</p>
        <h2 className="mt-1 text-sm font-semibold text-slate-50">
          最近の傾向からみたアドバイス
        </h2>
      </div>

      <div className="mb-4">
        <p className="text-sm text-slate-100 whitespace-pre-line">{body}</p>
      </div>

      <div>
        <p className="text-xs font-semibold text-emerald-400 mb-1">
          今日から試せる具体的なアクション
        </p>
        {tips.length === 0 ? (
          <p className="text-xs text-slate-500">
            特に具体的なアクションはありません。
          </p>
        ) : (
          <ul className="space-y-1">
            {tips.map((tip, idx) => (
              <li key={idx} className="text-xs text-slate-200 leading-relaxed">
                ・{tip}
              </li>
            ))}
          </ul>
        )}
      </div>
    </Card>
  );
}
