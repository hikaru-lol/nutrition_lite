/**
 * TodayPageTest - Phase 3統合テスト用コンポーネント
 *
 * Context統合が正しく動作するかを確認するためのテストページ
 */

'use client';

import { TodayPageProvider, useTodayPageContext } from '../context/TodayPageContext';
import { LoadingState } from '@/shared/ui/Status/LoadingState';
import { ErrorState } from '@/shared/ui/Status/ErrorState';

// ========================================
// Test Component
// ========================================

interface TodayPageTestProps {
  date: string;
}

export function TodayPageTest({ date }: TodayPageTestProps) {
  return (
    <TodayPageProvider date={date}>
      <TodayPageTestContent />
    </TodayPageProvider>
  );
}

// ========================================
// Test Content Component
// ========================================

function TodayPageTestContent() {
  const context = useTodayPageContext();

  if (context.isLoading) {
    return <LoadingState label="TodayPage Context テスト中..." />;
  }

  if (context.hasError) {
    return (
      <ErrorState
        title="Context エラー"
        message="データの取得に失敗しました"
      />
    );
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">TodayPage Context テスト</h1>

      {/* 日付情報 */}
      <TestSection title="基本情報">
        <TestItem label="日付" value={context.date} />
        <TestItem label="ローディング" value={context.isLoading.toString()} />
        <TestItem label="エラー" value={context.hasError.toString()} />
      </TestSection>

      {/* 食事データ */}
      <TestSection title="食事データ">
        <TestItem label="食事アイテム数" value={context.meals.items.length.toString()} />
        <TestItem label="食事ローディング" value={context.meals.isLoading.toString()} />
        <TestItem label="食事エラー" value={context.meals.isError.toString()} />
        <button
          onClick={() => console.log('食事データ:', context.meals.items)}
          className="px-3 py-1 bg-blue-500 text-white rounded text-sm"
        >
          食事データをコンソール出力
        </button>
      </TestSection>

      {/* 目標データ */}
      <TestSection title="目標データ">
        <TestItem
          label="アクティブ目標"
          value={context.targets.activeTarget ? '設定済み' : '未設定'}
        />
        <TestItem
          label="栄養素進捗数"
          value={context.targets.nutrientProgress.length.toString()}
        />
        <TestItem label="目標ローディング" value={context.targets.isLoading.toString()} />
        <button
          onClick={() => console.log('目標データ:', context.targets)}
          className="px-3 py-1 bg-green-500 text-white rounded text-sm"
        >
          目標データをコンソール出力
        </button>
      </TestSection>

      {/* プロフィールデータ */}
      <TestSection title="プロフィールデータ">
        <TestItem
          label="プロフィール"
          value={context.profile.profile ? '設定済み' : '未設定'}
        />
        <TestItem
          label="1日の食事回数"
          value={context.profile.mealsPerDay.toString()}
        />
        <TestItem label="プロフィールローディング" value={context.profile.isLoading.toString()} />
      </TestSection>

      {/* 栄養データ */}
      <TestSection title="栄養データ">
        <TestItem
          label="選択された食事"
          value={context.nutrition.selectedMeal ? '選択中' : '未選択'}
        />
        <TestItem
          label="栄養キャッシュサイズ"
          value={context.nutrition.nutritionCache.size.toString()}
        />
        <button
          onClick={async () => {
            try {
              const result = await context.nutrition.analyze('main', 1);
              console.log('栄養分析結果:', result);
            } catch (error) {
              console.error('栄養分析エラー:', error);
            }
          }}
          className="px-3 py-1 bg-yellow-500 text-white rounded text-sm"
        >
          栄養分析テスト
        </button>
      </TestSection>

      {/* レポートデータ */}
      <TestSection title="レポートデータ">
        <TestItem
          label="日次レポート"
          value={context.reports.dailyReport ? '生成済み' : '未生成'}
        />
        <TestItem label="レポート生成中" value={context.reports.isGenerating.toString()} />
        <TestItem
          label="食事完了度検証"
          value={context.reports.validationState.isMealCompletionValid.toString()}
        />
        <button
          onClick={() => {
            if (context.reports.validationState.hasEnoughData) {
              context.reports.generateReport(context.date);
            } else {
              alert('レポート生成には十分な食事データが必要です');
            }
          }}
          className="px-3 py-1 bg-purple-500 text-white rounded text-sm"
        >
          レポート生成テスト
        </button>
      </TestSection>

      {/* モーダルデータ */}
      <TestSection title="モーダル管理">
        <TestItem label="食事追加モーダル" value={context.modals.addModal.isOpen.toString()} />
        <TestItem label="食事編集モーダル" value={context.modals.editModal.isOpen.toString()} />
        <TestItem label="栄養詳細モーダル" value={context.modals.nutritionModal.isOpen.toString()} />
        <TestItem label="推奨モーダル" value={context.modals.recommendationModal.isOpen.toString()} />
        <div className="flex gap-2 mt-2">
          <button
            onClick={() => context.modals.openAddModal('main', 1)}
            className="px-3 py-1 bg-indigo-500 text-white rounded text-sm"
          >
            追加モーダル開く
          </button>
          <button
            onClick={() => context.modals.closeAllModals()}
            className="px-3 py-1 bg-red-500 text-white rounded text-sm"
          >
            全モーダル閉じる
          </button>
        </div>
      </TestSection>

      {/* 統合機能テスト */}
      <TestSection title="統合機能テスト">
        <button
          onClick={() => {
            console.log('=== TodayPage Context 完全ダンプ ===');
            console.log('Context Value:', context);
            console.log('=== ダンプ終了 ===');
          }}
          className="px-4 py-2 bg-gray-700 text-white rounded"
        >
          全データをコンソール出力
        </button>
      </TestSection>
    </div>
  );
}

// ========================================
// Helper Components
// ========================================

interface TestSectionProps {
  title: string;
  children: React.ReactNode;
}

function TestSection({ title, children }: TestSectionProps) {
  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <h2 className="text-lg font-semibold mb-3 text-gray-800">{title}</h2>
      <div className="space-y-2">
        {children}
      </div>
    </div>
  );
}

interface TestItemProps {
  label: string;
  value: string;
}

function TestItem({ label, value }: TestItemProps) {
  return (
    <div className="flex justify-between items-center py-1">
      <span className="text-sm font-medium text-gray-600">{label}:</span>
      <span className="text-sm text-gray-900 font-mono">{value}</span>
    </div>
  );
}