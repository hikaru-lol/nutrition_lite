// components/reports/ReportActions.tsx
'use client';

import { Button } from '@/components/ui/button';
import type { Plan } from '@/lib/hooks/useDailyReport';

type ReportActionsProps = {
  plan: Plan;
  hasReport: boolean;
  isCompleted: boolean;
  isGenerating: boolean;
  onGenerate: () => Promise<void> | void;
  errorMessage?: string | null;
};

export function ReportActions({
  plan,
  hasReport,
  isCompleted,
  isGenerating,
  onGenerate,
  errorMessage,
}: ReportActionsProps) {
  const locked = plan === 'free';

  if (locked) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
        <p className="text-xs text-slate-400 mb-2">
          日次レポートの生成は、有料プランまたはトライアル期間中にご利用いただけます。
        </p>
        <p className="text-xs text-slate-500">
          プラン画面からアップグレードすると、毎日のレポートと提案機能が利用できます。
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {errorMessage && (
        <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/40 rounded-lg px-3 py-2">
          {errorMessage}
        </p>
      )}

      {!hasReport && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm text-slate-100">
              この日の記録からレポートを生成します。
            </p>
            <p className="mt-1 text-xs text-slate-400">
              メインの食事回数がすべて記録されている必要があります。
            </p>
          </div>
          <Button
            size="sm"
            disabled={!isCompleted || isGenerating}
            onClick={onGenerate}
          >
            {isGenerating
              ? 'レポート生成中...'
              : isCompleted
              ? 'レポートを生成する'
              : '記録が完了していません'}
          </Button>
        </div>
      )}

      {hasReport && (
        <p className="text-[11px] text-slate-500">
          このレポートは生成時点の情報に基づいています。必要であれば、
          食事内容を調整したうえで新しい日付のレポートを作成してください。
        </p>
      )}
    </div>
  );
}
