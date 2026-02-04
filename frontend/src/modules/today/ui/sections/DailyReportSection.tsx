/**
 * DailyReportSection - 日次レポート表示セクション
 *
 * 責務:
 * - Context経由でのレポートデータ取得
 * - レポート生成の管理とUIフィードバック
 * - プロップスレスな実装
 */

'use client';

import { useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, RefreshCw, AlertCircle, CheckCircle2 } from 'lucide-react';
import { DailyReportCard } from '@/shared/ui/cards/DailyReportCard';
import {
  useTodayReports,
  useTodayMeals,
  useTodayProfile,
} from '../../context/TodayPageContext';

// ========================================
// Component Interface
// ========================================

interface DailyReportSectionProps {
  className?: string;
}

// ========================================
// Main Component
// ========================================

export function DailyReportSection({ className }: DailyReportSectionProps = {}) {
  // Context経由で各ドメインデータを取得
  const reports = useTodayReports();
  const meals = useTodayMeals();
  const profile = useTodayProfile();

  // ========================================
  // Event Handlers
  // ========================================

  // レポート生成ハンドラー
  const handleGenerateReport = useCallback(async () => {
    try {
      await reports.generateReport(new Date().toISOString().split('T')[0]);
    } catch (error) {
      console.error('レポート生成エラー:', error);
    }
  }, [reports.generateReport]);

  // レポート再読み込みハンドラー
  const handleRefreshReport = useCallback(() => {
    reports.fetchReport(new Date().toISOString().split('T')[0]);
  }, [reports.fetchReport]);

  // ========================================
  // Validation & Status
  // ========================================

  const validationState = reports.validationState;
  const canGenerateReport = validationState.hasEnoughData && !reports.isGenerating;

  // ========================================
  // Render
  // ========================================

  return (
    <div className={className} data-tour="daily-report">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center justify-between">
            <span>今日のレポート</span>
            <div className="flex gap-2">
              {reports.dailyReport && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRefreshReport}
                  disabled={reports.isLoading}
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
              )}
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* バリデーション状態の表示 */}
          <ValidationStatusAlert
            validationState={validationState}
            isGenerating={reports.isGenerating}
            mealCount={meals.items.length}
            mealsPerDay={profile.mealsPerDay}
          />

          {/* レポート表示エリア */}
          <div>
            {reports.isLoading && !reports.dailyReport && (
              <ReportLoadingSkeleton />
            )}

            {reports.isError && (
              <div className="text-center py-8">
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    レポートの読み込みに失敗しました
                  </AlertDescription>
                </Alert>
                <Button
                  variant="outline"
                  className="mt-4"
                  onClick={handleRefreshReport}
                >
                  再試行
                </Button>
              </div>
            )}

            {!reports.isLoading && !reports.isError && !reports.dailyReport && (
              <div className="text-center py-8">
                <div className="mb-4">
                  <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                    <AlertCircle className="h-8 w-8 text-gray-400" />
                  </div>
                </div>
                <h3 className="text-lg font-medium mb-2">レポートが生成されていません</h3>
                <p className="text-muted-foreground mb-4">
                  食事データからAIレポートを生成できます
                </p>
                <Button
                  onClick={handleGenerateReport}
                  disabled={!canGenerateReport}
                  className="min-w-[120px]"
                >
                  {reports.isGenerating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      生成中...
                    </>
                  ) : (
                    'レポート生成'
                  )}
                </Button>
              </div>
            )}

            {reports.dailyReport && (
              <div className="space-y-4">
                <DailyReportCard
                  report={reports.dailyReport}
                  isLoading={reports.isLoading}
                />

                {/* レポート更新ボタン */}
                <div className="text-center pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleGenerateReport}
                    disabled={reports.isGenerating}
                  >
                    {reports.isGenerating ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        更新中...
                      </>
                    ) : (
                      'レポート更新'
                    )}
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* 生成エラーメッセージ */}
          {reports.generateError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                レポートの生成に失敗しました: {reports.generateError.message || '不明なエラー'}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// ========================================
// Helper Components
// ========================================

interface ValidationStatusAlertProps {
  validationState: {
    isMealCompletionValid: boolean;
    hasEnoughData: boolean;
    missingMealsCount: number;
  };
  isGenerating: boolean;
  mealCount: number;
  mealsPerDay: number;
}

function ValidationStatusAlert({
  validationState,
  isGenerating,
  mealCount,
  mealsPerDay,
}: ValidationStatusAlertProps) {
  if (isGenerating) {
    return (
      <Alert>
        <Loader2 className="h-4 w-4 animate-spin" />
        <AlertDescription>
          AIがレポートを生成しています...
        </AlertDescription>
      </Alert>
    );
  }

  if (!validationState.hasEnoughData) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          レポート生成には最低 {Math.floor(mealsPerDay / 2)} 回の食事記録が必要です
          （現在: {mealCount} / {mealsPerDay}）
        </AlertDescription>
      </Alert>
    );
  }

  if (validationState.isMealCompletionValid) {
    return (
      <Alert className="border-green-200 bg-green-50">
        <CheckCircle2 className="h-4 w-4 text-green-600" />
        <AlertDescription className="text-green-800">
          レポート生成可能（食事記録: {mealCount} / {mealsPerDay}）
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <Alert className="border-yellow-200 bg-yellow-50">
      <AlertCircle className="h-4 w-4 text-yellow-600" />
      <AlertDescription className="text-yellow-800">
        食事記録が少なめです。より正確なレポートのため追加記録をお勧めします
        （現在: {mealCount} / {mealsPerDay}）
      </AlertDescription>
    </Alert>
  );
}

function ReportLoadingSkeleton() {
  return (
    <div className="space-y-4">
      <div className="animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-3 bg-gray-200 rounded w-full"></div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ========================================
// 軽量版・特殊用途バリエーション
// ========================================

/**
 * レポート状況のみの軽量版
 */
export function ReportStatusSection({ className }: DailyReportSectionProps = {}) {
  const reports = useTodayReports();

  if (reports.isLoading) {
    return (
      <div className={className}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-32"></div>
        </div>
      </div>
    );
  }

  const getStatusText = () => {
    if (reports.isGenerating) return '生成中';
    if (reports.dailyReport) return '生成済み';
    if (reports.validationState.hasEnoughData) return '生成可能';
    return '記録不足';
  };

  const getStatusColor = () => {
    if (reports.isGenerating) return 'text-blue-600';
    if (reports.dailyReport) return 'text-green-600';
    if (reports.validationState.hasEnoughData) return 'text-yellow-600';
    return 'text-gray-600';
  };

  return (
    <div className={className}>
      <div className="text-sm">
        <span className="text-muted-foreground">レポート: </span>
        <span className={`font-medium ${getStatusColor()}`}>
          {getStatusText()}
        </span>
      </div>
    </div>
  );
}

/**
 * レポート生成ボタンのみ
 */
export function ReportGenerateSection({ className }: DailyReportSectionProps = {}) {
  const reports = useTodayReports();

  const handleGenerateReport = useCallback(async () => {
    try {
      await reports.generateReport(new Date().toISOString().split('T')[0]);
    } catch (error) {
      console.error('レポート生成エラー:', error);
    }
  }, [reports.generateReport]);

  const canGenerate = reports.validationState.hasEnoughData && !reports.isGenerating;

  return (
    <div className={className}>
      <Button
        onClick={handleGenerateReport}
        disabled={!canGenerate}
        size="sm"
        variant={reports.dailyReport ? "outline" : "default"}
        className="w-full"
      >
        {reports.isGenerating ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            生成中...
          </>
        ) : (
          reports.dailyReport ? 'レポート更新' : 'レポート生成'
        )}
      </Button>
    </div>
  );
}

// ========================================
// プレビュー・デバッグ用コンポーネント
// ========================================

/**
 * レポートデータのプレビュー表示（開発用）
 */
export function DailyReportPreview() {
  const reports = useTodayReports();
  const meals = useTodayMeals();

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <details className="p-4 border rounded-lg">
      <summary className="cursor-pointer font-medium">
        Daily Report Debug Info
      </summary>
      <div className="mt-2 space-y-2 text-xs">
        <div>
          <strong>Daily Report:</strong> {reports.dailyReport ? '生成済み' : 'なし'}
        </div>
        <div>
          <strong>Enhanced Report:</strong> {reports.enhancedReport ? '生成済み' : 'なし'}
        </div>
        <div>
          <strong>Loading:</strong> {reports.isLoading.toString()}
        </div>
        <div>
          <strong>Error:</strong> {reports.isError.toString()}
        </div>
        <div>
          <strong>Generating:</strong> {reports.isGenerating.toString()}
        </div>
        <div>
          <strong>Validation State:</strong>
          <pre className="mt-1 p-2 bg-gray-100 rounded">
            {JSON.stringify(reports.validationState, null, 2)}
          </pre>
        </div>
        <div>
          <strong>Meal Count:</strong> {meals.items.length}
        </div>
        {reports.generateError && (
          <div>
            <strong>Generate Error:</strong>
            <pre className="mt-1 p-2 bg-red-100 rounded text-red-800">
              {JSON.stringify(reports.generateError, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </details>
  );
}