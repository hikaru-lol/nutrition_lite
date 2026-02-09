'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Lock, Sparkles, ChefHat, AlertTriangle } from 'lucide-react';
import type { DailyNutritionReport } from '@/modules/nutrition/contract/nutritionContract';

// ========================================
// Types
// ========================================

interface DailyReportCardProps {
  date: string;
  dailyReport: {
    report: DailyNutritionReport | null;
    isLoading: boolean;
    isError: boolean;
    isGenerating: boolean;
    generateError: Error | null;
    onGenerate: () => void;
    onFetch: () => void;
  };
  mealCompletion: {
    isValid: boolean;
    status: { completed: number; required: number };
    missingCount: number;
    hasEnoughData: boolean;
  };
}

export function DailyReportCard({
  date,
  dailyReport,
  mealCompletion,
}: DailyReportCardProps) {
  // 選択した日付が今日かどうかを判定
  const isToday = date === new Date().toLocaleDateString('sv-SE'); // YYYY-MM-DD format
  const displayDate = isToday ? '今日' : new Date(date).toLocaleDateString('ja-JP', {
    month: 'long',
    day: 'numeric'
  });
  return (
    <div className="relative">
      {/* Background glow effect */}
      <div className="absolute -top-4 -right-4 w-24 h-24 bg-purple-500/10 rounded-full blur-3xl" />
      <div className="absolute -bottom-4 -left-4 w-20 h-20 bg-indigo-500/8 rounded-full blur-3xl" />

      <Card className="relative z-10 transition-all duration-500 hover:shadow-lg">
        <CardHeader>
          <CardTitle className="bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
            {displayDate}の日次レポート
          </CardTitle>
        </CardHeader>
      <CardContent>
        {dailyReport.isLoading ? (
          <div className="text-sm text-muted-foreground">読み込み中...</div>
        ) : dailyReport.report ? (
          // レポートが存在する場合の表示
          <div className="space-y-3">
            <div className="text-sm">
              <div className="whitespace-pre-line">{dailyReport.report.summary}</div>
            </div>
            <div className="text-xs text-muted-foreground">
              生成日: {new Date(dailyReport.report.created_at).toLocaleDateString()}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={dailyReport.onGenerate}
              disabled={dailyReport.isGenerating}
              className="transition-all duration-200 hover:bg-purple-50 hover:border-purple-300 dark:hover:bg-purple-950/20 dark:hover:border-purple-700"
            >
              {dailyReport.isGenerating ? (
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-3 w-3 border border-current border-t-transparent" />
                  <span>レポート更新中...</span>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Sparkles className="h-3 w-3" />
                  <span>レポートを更新</span>
                </div>
              )}
            </Button>
          </div>
        ) : (
          // レポートが未生成の場合
          <div className="space-y-4">
            {/* State A: ロック状態（データ不足） */}
            {!mealCompletion.hasEnoughData && (
              <div className="relative p-6 rounded-xl bg-amber-500/5 border border-amber-200/50 dark:bg-amber-950/10 dark:border-amber-800/30">
                <div className="absolute top-4 right-4">
                  <Lock className="h-5 w-5 text-amber-600/60 dark:text-amber-400/60" />
                </div>
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-amber-100 dark:bg-amber-900/30">
                    <ChefHat className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                  </div>
                  <div>
                    <h4 className="font-medium text-amber-900 dark:text-amber-100 mb-1">
                      分析ロック中
                    </h4>
                    <p className="text-sm text-amber-700 dark:text-amber-300">
                      あと<span className="font-semibold">{mealCompletion.missingCount}食</span>の記録でAI分析が利用できます
                    </p>
                    <div className="mt-2 flex items-center gap-2">
                      <div className="h-2 w-24 bg-amber-200 dark:bg-amber-800/40 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-amber-500 dark:bg-amber-400 rounded-full transition-all duration-300"
                          style={{
                            width: `${(mealCompletion.status.completed / mealCompletion.status.required) * 100}%`
                          }}
                        />
                      </div>
                      <span className="text-xs font-mono text-amber-600 dark:text-amber-400">
                        {mealCompletion.status.completed}/{mealCompletion.status.required}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* State B: Ready状態（生成可能） */}
            {mealCompletion.hasEnoughData && (
              <div className="space-y-4">
                <div className="text-center">
                  <p className="text-sm text-emerald-700 dark:text-emerald-300 font-medium">
                    🎉 {displayDate}の食事記録が揃いました
                  </p>
                </div>

                <button
                  onClick={dailyReport.onGenerate}
                  disabled={dailyReport.isGenerating}
                  className="group relative w-full overflow-hidden rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 p-4 text-white shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                >
                  <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  <div className="relative flex items-center justify-center gap-2">
                    {dailyReport.isGenerating ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                        <span className="font-semibold">AI分析中...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-5 w-5" />
                        <span className="font-semibold">AI日次レポートを生成</span>
                      </>
                    )}
                  </div>
                </button>
              </div>
            )}

            {/* State C: エラー表示 */}
            {dailyReport.generateError && (
              <div className="flex items-start gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800">
                <AlertTriangle className="h-4 w-4 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                <div className="text-sm">
                  <div className="font-medium text-red-800 dark:text-red-200 mb-1">
                    生成に失敗しました
                  </div>
                  <div className="text-red-700 dark:text-red-300">
                    食事ログが完了しているか確認してください。
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        </CardContent>
      </Card>
    </div>
  );
}