/**
 * TodayPageMigrationTest - 段階的移行テスト用コンポーネント
 *
 * 責務:
 * - 新旧アーキテクチャの並行テスト
 * - 段階的移行フラグの動作確認
 * - パフォーマンス比較
 */

'use client';

import { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
// import { Switch } from '@/components/ui/switch'; // 一時的に無効化
import { Badge } from '@/components/ui/badge';
import { TodayPageContent } from './TodayPageContent';
import { TodayPageLayout, type MigrationFlags } from './TodayPageLayout';
import { formatLocalDateYYYYMMDD } from '../types/todayTypes';

// ========================================
// Component Interface
// ========================================

interface TodayPageMigrationTestProps {
  date?: string;
  className?: string;
}

// ========================================
// Main Component
// ========================================

export function TodayPageMigrationTest({
  date: propDate,
  className,
}: TodayPageMigrationTestProps = {}) {
  // テスト用の日付設定
  const date = propDate ?? formatLocalDateYYYYMMDD(new Date());

  // 表示モード制御
  const [viewMode, setViewMode] = useState<'legacy' | 'new' | 'side-by-side'>('side-by-side');

  // 移行フラグ制御
  const [migrationFlags, setMigrationFlags] = useState<MigrationFlags>({
    useDailySummarySection: true,
    useMealListSection: true,
    useTargetProgressSection: true,
    useDailyReportSection: true,
    useModalsContainer: true,
    useFullNewLayout: false,
  });

  // パフォーマンス測定
  const [performanceData, setPerformanceData] = useState<{
    legacy?: number;
    new?: number;
  }>({});

  // ========================================
  // Event Handlers
  // ========================================

  const handleFlagChange = (flag: keyof MigrationFlags, value: boolean) => {
    setMigrationFlags(prev => ({ ...prev, [flag]: value }));
  };

  const handleResetFlags = () => {
    setMigrationFlags({
      useDailySummarySection: false,
      useMealListSection: false,
      useTargetProgressSection: false,
      useDailyReportSection: false,
      useModalsContainer: false,
      useFullNewLayout: false,
    });
  };

  const handleEnableAll = () => {
    setMigrationFlags({
      useDailySummarySection: true,
      useMealListSection: true,
      useTargetProgressSection: true,
      useDailyReportSection: true,
      useModalsContainer: true,
      useFullNewLayout: true,
    });
  };

  const measurePerformance = (type: 'legacy' | 'new') => {
    const startTime = performance.now();
    // 実際のパフォーマンス測定はレンダリング後に行う
    setTimeout(() => {
      const endTime = performance.now();
      setPerformanceData(prev => ({
        ...prev,
        [type]: endTime - startTime,
      }));
    }, 100);
  };

  // ========================================
  // Computed Values
  // ========================================

  const migrationProgress = useMemo(() => {
    const enabledCount = Object.values(migrationFlags).filter(Boolean).length;
    const totalCount = Object.keys(migrationFlags).length;
    return (enabledCount / totalCount) * 100;
  }, [migrationFlags]);

  const flagDescriptions: Record<keyof MigrationFlags, string> = {
    useDailySummarySection: '日次サマリーセクション',
    useMealListSection: '食事リストセクション',
    useTargetProgressSection: '目標進捗セクション',
    useDailyReportSection: '日次レポートセクション',
    useModalsContainer: 'モーダル統合コンテナ',
    useFullNewLayout: '完全新レイアウト',
  };

  // ========================================
  // Render
  // ========================================

  if (process.env.NODE_ENV !== 'development') {
    return (
      <div className={className}>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center text-muted-foreground">
              このコンポーネントは開発環境でのみ利用可能です
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* 制御パネル */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            TodayPage 移行テスト
            <Badge variant="outline">
              進捗 {migrationProgress.toFixed(0)}%
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 表示モード選択 */}
          <div>
            <h4 className="text-sm font-medium mb-2">表示モード</h4>
            <div className="flex gap-2">
              <Button
                variant={viewMode === 'legacy' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('legacy')}
              >
                Legacy のみ
              </Button>
              <Button
                variant={viewMode === 'new' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('new')}
              >
                New のみ
              </Button>
              <Button
                variant={viewMode === 'side-by-side' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('side-by-side')}
              >
                並行比較
              </Button>
            </div>
          </div>

          {/* 移行フラグ制御 */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-medium">移行フラグ</h4>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={handleResetFlags}>
                  全てOFF
                </Button>
                <Button variant="outline" size="sm" onClick={handleEnableAll}>
                  全てON
                </Button>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {Object.entries(migrationFlags).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium text-sm">
                      {flagDescriptions[key as keyof MigrationFlags]}
                    </div>
                    <div className="text-xs text-muted-foreground">{key}</div>
                  </div>
                  <SimpleToggle
                    checked={value}
                    onChange={(checked) =>
                      handleFlagChange(key as keyof MigrationFlags, checked)
                    }
                  />
                </div>
              ))}
            </div>
          </div>

          {/* パフォーマンス情報 */}
          {(performanceData.legacy || performanceData.new) && (
            <div>
              <h4 className="text-sm font-medium mb-2">パフォーマンス</h4>
              <div className="grid grid-cols-2 gap-3">
                {performanceData.legacy && (
                  <div className="p-3 border rounded-lg">
                    <div className="text-sm font-medium">Legacy</div>
                    <div className="text-xs text-muted-foreground">
                      {performanceData.legacy.toFixed(2)}ms
                    </div>
                  </div>
                )}
                {performanceData.new && (
                  <div className="p-3 border rounded-lg">
                    <div className="text-sm font-medium">New</div>
                    <div className="text-xs text-muted-foreground">
                      {performanceData.new.toFixed(2)}ms
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* コンテンツ表示エリア */}
      <div className="space-y-6">
        {viewMode === 'side-by-side' && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {/* Legacy Implementation */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  Legacy Implementation
                  <Badge variant="secondary">既存</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div onLoad={() => measurePerformance('legacy')}>
                  <TodayPageContent date={date} />
                </div>
              </CardContent>
            </Card>

            {/* New Implementation */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  New Implementation
                  <Badge variant="default">新アーキテクチャ</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div onLoad={() => measurePerformance('new')}>
                  <TodayPageLayout date={date} migrationFlags={migrationFlags} />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {viewMode === 'legacy' && (
          <Card>
            <CardHeader>
              <CardTitle>Legacy Implementation</CardTitle>
            </CardHeader>
            <CardContent>
              <TodayPageContent date={date} />
            </CardContent>
          </Card>
        )}

        {viewMode === 'new' && (
          <Card>
            <CardHeader>
              <CardTitle>New Implementation</CardTitle>
            </CardHeader>
            <CardContent>
              <TodayPageLayout date={date} migrationFlags={migrationFlags} />
            </CardContent>
          </Card>
        )}
      </div>

      {/* デバッグ情報 */}
      <details className="bg-gray-50 rounded-lg">
        <summary className="p-4 cursor-pointer font-medium">
          デバッグ情報
        </summary>
        <div className="p-4 pt-0 space-y-3 text-sm">
          <div>
            <strong>Date:</strong> {date}
          </div>
          <div>
            <strong>View Mode:</strong> {viewMode}
          </div>
          <div>
            <strong>Migration Progress:</strong> {migrationProgress.toFixed(1)}%
          </div>
          <div>
            <strong>Active Flags:</strong>
            <pre className="mt-2 p-3 bg-white rounded border overflow-auto">
              {JSON.stringify(migrationFlags, null, 2)}
            </pre>
          </div>
        </div>
      </details>
    </div>
  );
}

// ========================================
// Simple Toggle Component (Switch replacement)
// ========================================

interface SimpleToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
}

function SimpleToggle({ checked, onChange }: SimpleToggleProps) {
  return (
    <label className="flex items-center cursor-pointer">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="sr-only"
      />
      <div
        className={`relative w-11 h-6 rounded-full transition-colors ${
          checked ? 'bg-blue-600' : 'bg-gray-200'
        }`}
      >
        <div
          className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
            checked ? 'translate-x-5' : 'translate-x-0'
          }`}
        />
      </div>
    </label>
  );
}