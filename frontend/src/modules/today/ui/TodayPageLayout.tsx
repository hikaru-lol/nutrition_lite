/**
 * TodayPageLayout - 段階的移行用レイアウトコンポーネント
 *
 * 責務:
 * - 新旧コンポーネントの統合管理
 * - 段階的移行のための機能フラグサポート
 * - Context統合の最終実装
 */

'use client';

import { useMemo } from 'react';
import { TodayPageProvider } from '../context/TodayPageContext';
import { DailySummarySection } from './sections/DailySummarySection';
import { MealListSection } from './sections/MealListSection';
import { TargetProgressSection } from './sections/TargetProgressSection';
import { DailyReportSection } from './sections/DailyReportSection';
import { TodayModalsContainer } from './sections/TodayModalsContainer';

// 既存コンポーネントとの互換性のための一時import
// Phase 6で削除予定
import { TodayPageContent } from './TodayPageContent';

// ========================================
// Migration Flags
// ========================================

interface MigrationFlags {
  useDailySummarySection: boolean;
  useMealListSection: boolean;
  useTargetProgressSection: boolean;
  useDailyReportSection: boolean;
  useModalsContainer: boolean;
  useFullNewLayout: boolean;
}

// デフォルト設定: 段階的移行
const defaultMigrationFlags: MigrationFlags = {
  useDailySummarySection: true,   // Phase 5.1: 日次サマリーから開始
  useMealListSection: false,      // Phase 5.2: 食事リスト
  useTargetProgressSection: false, // Phase 5.3: 目標進捗
  useDailyReportSection: false,   // Phase 5.4: レポート
  useModalsContainer: true,       // Phase 5.5: モーダル統合
  useFullNewLayout: false,        // Phase 6: 完全移行
};

// 環境変数での設定オーバーライド（開発時のテスト用）
const getEnvironmentFlags = (): Partial<MigrationFlags> => {
  if (typeof window === 'undefined') return {};

  try {
    const envFlags = process.env.NEXT_PUBLIC_TODAY_MIGRATION_FLAGS;
    return envFlags ? JSON.parse(envFlags) : {};
  } catch {
    return {};
  }
};

// ========================================
// Component Interface
// ========================================

interface TodayPageLayoutProps {
  date: string;
  className?: string;
  migrationFlags?: Partial<MigrationFlags>;
}

// ========================================
// Main Component
// ========================================

export function TodayPageLayout({
  date,
  className,
  migrationFlags: customFlags,
}: TodayPageLayoutProps) {
  // フラグの統合: デフォルト → 環境変数 → props
  const flags = useMemo(() => ({
    ...defaultMigrationFlags,
    ...getEnvironmentFlags(),
    ...customFlags,
  }), [customFlags]);

  // Phase 6: 完全移行版の早期リターン
  if (flags.useFullNewLayout) {
    return (
      <TodayPageProvider date={date}>
        <div className={className}>
          <FullNewLayout date={date} />
        </div>
      </TodayPageProvider>
    );
  }

  // Phase 5: 段階的移行版
  return (
    <TodayPageProvider date={date}>
      <div className={className}>
        <HybridLayout date={date} flags={flags} />
      </div>
    </TodayPageProvider>
  );
}

// ========================================
// Layout Variants
// ========================================

/**
 * Phase 5: ハイブリッドレイアウト（新旧混在）
 */
function HybridLayout({ date, flags }: { date: string; flags: MigrationFlags }) {
  return (
    <div className="space-y-6">
      {/* 新しい日次サマリー or 既存実装 */}
      {flags.useDailySummarySection ? (
        <DailySummarySection />
      ) : (
        <LegacySummaryWrapper date={date} />
      )}

      {/* 新しい食事リスト or 既存実装 */}
      {flags.useMealListSection ? (
        <MealListSection />
      ) : (
        <LegacyMealListWrapper date={date} />
      )}

      {/* 新しい目標進捗 or 既存実装 */}
      {flags.useTargetProgressSection ? (
        <TargetProgressSection />
      ) : (
        <LegacyTargetProgressWrapper date={date} />
      )}

      {/* 新しいレポート or 既存実装 */}
      {flags.useDailyReportSection ? (
        <DailyReportSection />
      ) : (
        <LegacyReportWrapper date={date} />
      )}

      {/* モーダルコンテナ（統合 or 既存） */}
      {flags.useModalsContainer ? (
        <TodayModalsContainer date={date} />
      ) : (
        <LegacyModalsWrapper date={date} />
      )}

      {/* 開発時のデバッグ情報 */}
      {process.env.NODE_ENV === 'development' && (
        <MigrationDebugPanel flags={flags} date={date} />
      )}
    </div>
  );
}

/**
 * Phase 6: 完全新レイアウト
 */
function FullNewLayout({ date }: { date: string }) {
  return (
    <div className="space-y-6">
      {/* 新しいアーキテクチャによる完全実装 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <DailySummarySection />
          <TargetProgressSection />
        </div>
        <div className="space-y-6">
          <MealListSection />
          <DailyReportSection />
        </div>
      </div>

      {/* 統合モーダル */}
      <TodayModalsContainer date={date} />
    </div>
  );
}

// ========================================
// Legacy Wrappers（Phase 6で削除予定）
// ========================================

/**
 * 既存実装への一時的ブリッジコンポーネント群
 * これらは段階的移行中のみ使用し、Phase 6で削除
 */

function LegacySummaryWrapper({ date }: { date: string }) {
  return (
    <div data-legacy="summary">
      {/* 既存のTodayPageContentから日次サマリー部分を抽出 */}
      {/* TODO: Phase 6で削除 */}
      <div className="p-4 border border-yellow-200 bg-yellow-50 rounded-lg">
        <div className="text-sm text-yellow-800">
          Legacy Summary Component (Phase 5)
        </div>
      </div>
    </div>
  );
}

function LegacyMealListWrapper({ date }: { date: string }) {
  return (
    <div data-legacy="meal-list">
      {/* 既存のTodayPageContentから食事リスト部分を抽出 */}
      {/* TODO: Phase 6で削除 */}
      <div className="p-4 border border-yellow-200 bg-yellow-50 rounded-lg">
        <div className="text-sm text-yellow-800">
          Legacy Meal List Component (Phase 5)
        </div>
      </div>
    </div>
  );
}

function LegacyTargetProgressWrapper({ date }: { date: string }) {
  return (
    <div data-legacy="target-progress">
      {/* 既存のTodayPageContentから目標進捗部分を抽出 */}
      {/* TODO: Phase 6で削除 */}
      <div className="p-4 border border-yellow-200 bg-yellow-50 rounded-lg">
        <div className="text-sm text-yellow-800">
          Legacy Target Progress Component (Phase 5)
        </div>
      </div>
    </div>
  );
}

function LegacyReportWrapper({ date }: { date: string }) {
  return (
    <div data-legacy="report">
      {/* 既存のTodayPageContentからレポート部分を抽出 */}
      {/* TODO: Phase 6で削除 */}
      <div className="p-4 border border-yellow-200 bg-yellow-50 rounded-lg">
        <div className="text-sm text-yellow-800">
          Legacy Report Component (Phase 5)
        </div>
      </div>
    </div>
  );
}

function LegacyModalsWrapper({ date }: { date: string }) {
  return (
    <div data-legacy="modals">
      {/* 既存のモーダル実装 */}
      {/* TODO: Phase 6で削除 */}
      <div style={{ display: 'none' }} className="legacy-modals">
        Legacy Modals (Phase 5)
      </div>
    </div>
  );
}

// ========================================
// Development Tools
// ========================================

/**
 * 開発時の移行状況デバッグパネル
 */
function MigrationDebugPanel({
  flags,
  date,
}: {
  flags: MigrationFlags;
  date: string;
}) {
  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  const migrationProgress = Object.values(flags).filter(Boolean).length;
  const totalFlags = Object.keys(flags).length;

  return (
    <div className="fixed bottom-4 left-4 z-50 max-w-sm">
      <details className="bg-white border border-gray-300 rounded-lg shadow-lg">
        <summary className="p-3 cursor-pointer bg-gray-100 rounded-t-lg font-medium">
          Migration Debug ({migrationProgress}/{totalFlags})
        </summary>
        <div className="p-3 space-y-2 text-sm">
          <div className="font-medium">Date: {date}</div>

          <div className="space-y-1">
            {Object.entries(flags).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-gray-600">{key}:</span>
                <span className={value ? 'text-green-600' : 'text-red-600'}>
                  {value ? '✓ NEW' : '× OLD'}
                </span>
              </div>
            ))}
          </div>

          <div className="pt-2 border-t">
            <div className="text-xs text-gray-500">
              Progress: {((migrationProgress / totalFlags) * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      </details>
    </div>
  );
}

// ========================================
// Utility Functions
// ========================================

/**
 * 移行フラグ制御用のユーティリティフック
 */
export function useMigrationFlags(customFlags?: Partial<MigrationFlags>) {
  return useMemo(() => ({
    ...defaultMigrationFlags,
    ...getEnvironmentFlags(),
    ...customFlags,
  }), [customFlags]);
}

/**
 * 特定セクションが新実装を使用しているかチェック
 */
export function useIsNewImplementation(section: keyof MigrationFlags) {
  const flags = useMigrationFlags();
  return flags[section];
}

// ========================================
// Type Exports
// ========================================

export type { MigrationFlags };