// frontend/components/recommendations/RecommendationEmptyState.tsx
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';

export function RecommendationEmptyState() {
  const router = useRouter();

  return (
    <Card>
      <p className="text-sm text-slate-100 mb-2">
        まだ提案が生成されていません。
      </p>
      <p className="text-xs text-slate-400 mb-4">
        直近数日分の日次レポートが揃うと、ここに「次にどうすると良いか」の提案が表示されます。
      </p>
      <Button
        variant="secondary"
        size="sm"
        onClick={() =>
          router.push('/reports/daily/' + new Date().toISOString().slice(0, 10))
        }
      >
        今日の日次レポートを確認する
      </Button>
    </Card>
  );
}
