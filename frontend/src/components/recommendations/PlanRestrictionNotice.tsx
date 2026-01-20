// frontend/components/recommendations/PlanRestrictionNotice.tsx
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';

export function PlanRestrictionNotice() {
  const router = useRouter();

  return (
    <Card>
      <p className="text-sm text-slate-100 mb-2">
        提案機能は有料プランまたはトライアル期間中にご利用いただけます。
      </p>
      <p className="text-xs text-slate-400 mb-4">
        プランをアップグレードすることで、日次レポートに加え、最近の傾向にもとづいたより具体的なアドバイスを受け取ることができます。
      </p>
      <Button size="sm" onClick={() => router.push('/billing/upgrade')}>
        プランを確認する
      </Button>
    </Card>
  );
}
