'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Sparkles,
  CheckCircle,
  AlertTriangle,
  Target,
  Calendar,
  TrendingUp,
  Share2,
  Download
} from 'lucide-react';

import type { DailyNutritionReport } from '@/modules/nutrition/contract/nutritionContract';

interface EnhancedDailyReportCardProps {
  report: DailyNutritionReport;
  onShare?: () => void;
  onExport?: () => void;
  isLoading?: boolean;
}

export function EnhancedDailyReportCard({
  report,
  onShare,
  onExport,
  isLoading = false
}: EnhancedDailyReportCardProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    });
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ja-JP', {
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>日次レポート</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-muted-foreground">読み込み中...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden shadow-lg">
      {/* ヘッダー部分 - グラデーション背景 */}
      <CardHeader className="bg-gradient-to-r from-blue-600 to-purple-600 text-white relative">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-xl font-bold flex items-center gap-2">
              <Sparkles className="w-6 h-6" />
              栄養レポート
            </CardTitle>
            <div className="flex items-center gap-1 mt-1 text-blue-100">
              <Calendar className="w-4 h-4" />
              <span className="text-sm">{formatDate(report.date)}</span>
            </div>
          </div>

          {/* アクションボタン */}
          <div className="flex gap-2">
            {onShare && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onShare}
                className="text-white hover:bg-white/20 h-8 px-3"
              >
                <Share2 className="w-4 h-4" />
              </Button>
            )}
            {onExport && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onExport}
                className="text-white hover:bg-white/20 h-8 px-3"
              >
                <Download className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>

        {/* 生成日時 */}
        <div className="text-xs text-blue-100 mt-2">
          生成日時: {formatDateTime(report.created_at)}
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* AIサマリー部分 */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
          <h3 className="flex items-center gap-2 font-semibold text-blue-900 dark:text-blue-100 mb-3">
            <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            今日の栄養サマリー
          </h3>
          <p className="text-sm text-blue-800 dark:text-blue-200 leading-relaxed">
            {report.summary}
          </p>
        </div>

        {/* 良かった点 */}
        <div className="space-y-3">
          <h3 className="flex items-center gap-2 font-semibold text-green-900 dark:text-green-100">
            <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
            良かった点
          </h3>
          <div className="space-y-2">
            {report.good_points.map((point, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800"
              >
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                <p className="text-sm text-green-800 dark:text-green-200 leading-relaxed">
                  {point}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* 改善点 */}
        <div className="space-y-3">
          <h3 className="flex items-center gap-2 font-semibold text-amber-900 dark:text-amber-100">
            <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400" />
            改善点
          </h3>
          <div className="space-y-2">
            {report.improvement_points.map((point, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800"
              >
                <div className="w-2 h-2 bg-amber-500 rounded-full mt-2 flex-shrink-0" />
                <p className="text-sm text-amber-800 dark:text-amber-200 leading-relaxed">
                  {point}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* 明日のフォーカス */}
        <div className="space-y-3">
          <h3 className="flex items-center gap-2 font-semibold text-purple-900 dark:text-purple-100">
            <Target className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            明日のフォーカス
          </h3>
          <div className="space-y-2">
            {report.tomorrow_focus.map((focus, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800"
              >
                <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 flex-shrink-0" />
                <p className="text-sm text-purple-800 dark:text-purple-200 leading-relaxed">
                  {focus}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* フッター - 統計情報 */}
        <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <div className="flex items-center gap-4">
              <span>✅ 良い点: {report.good_points.length}件</span>
              <span>⚠️ 改善点: {report.improvement_points.length}件</span>
              <span>🎯 明日の目標: {report.tomorrow_focus.length}件</span>
            </div>
            <div className="text-right">
              AI栄養分析レポート
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}