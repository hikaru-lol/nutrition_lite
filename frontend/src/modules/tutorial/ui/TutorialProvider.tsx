/**
 * チュートリアル機能のプロバイダーコンポーネント
 * react-joyrideの統合とチュートリアル管理
 */

'use client';

import React, { useState, useCallback, useEffect } from 'react';
import Joyride, { CallBackProps, STATUS } from 'react-joyride';
import { useTutorialModel } from '../model/useTutorialModel';
import type { TutorialId } from '../contract/tutorialContract';

interface TutorialProviderProps {
  children: React.ReactNode;
}

export function TutorialProvider({ children }: TutorialProviderProps) {
  // チュートリアル実行状態
  const [runningTutorial, setRunningTutorial] = useState<TutorialId | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  // クライアントサイドでのみマウントを確認
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Hooksの順序を保つため、常に呼び出す
  const tutorialModel = useTutorialModel();

  /**
   * チュートリアルステップ定義
   */
  const getTutorialSteps = (tutorialId: TutorialId) => {
    switch (tutorialId) {
      case 'feature_today':
        return [
          {
            target: '[data-tour="today-title"]',
            content: 'ここはTodayページです。今日の栄養状況を一目で確認できます。',
            placement: 'bottom' as const,
            disableBeacon: true,
          },
          {
            target: '[data-tour="daily-summary"]',
            content: '本日のサマリーカードです。摂取カロリーや主要栄養素の情報が表示されます。',
            placement: 'bottom' as const,
          },
          {
            target: '[data-tour="meal-list"]',
            content: '食事ログ一覧です。朝食・昼食・夕食・間食を追加・編集できます。「+」ボタンで新しい食事を追加しましょう。',
            placement: 'top' as const,
          },
          {
            target: '[data-tour="target-progress"]',
            content: '目標達成度が表示されます。設定した栄養目標に対する今日の摂取状況を確認できます。',
            placement: 'top' as const,
          },
          {
            target: '[data-tour="daily-report"]',
            content: 'AI生成の日次レポートです。食事内容を分析してアドバイスをもらえます。「レポートを生成する」ボタンでAI分析を開始できます。',
            placement: 'top' as const,
          },
        ];

      case 'onboarding_profile':
        return [
          {
            target: '[data-tour="profile-title"]',
            content: 'プロフィール設定へようこそ！栄養目標を正確に計算するために、基本的な情報を入力しましょう。',
            placement: 'bottom' as const,
            disableBeacon: true,
          },
          {
            target: '[data-tour="profile-sex"]',
            content: '性別を選択してください。基礎代謝の計算に使用されます。',
            placement: 'bottom' as const,
          },
          {
            target: '[data-tour="profile-birthdate"]',
            content: '生年月日を入力してください。年齢に応じた栄養所要量を計算します。',
            placement: 'bottom' as const,
          },
          {
            target: '[data-tour="profile-body"]',
            content: '身長と体重を入力してください。BMIや基礎代謝量の計算に必要です。',
            placement: 'top' as const,
          },
          {
            target: '[data-tour="profile-submit"]',
            content: '情報を保存すると、次の目標設定ページに進みます。後からも変更できます。',
            placement: 'top' as const,
          },
        ];

      case 'onboarding_target':
        return [
          {
            target: '[data-tour="target-title"]',
            content: 'ターゲット生成ページへようこそ！プロフィール情報を元に、個人に最適化された栄養目標を自動生成します。',
            placement: 'bottom' as const,
            disableBeacon: true,
          },
          {
            target: '[data-tour="target-title-field"]',
            content: 'ターゲットの名前を入力してください。後から管理しやすいよう、分かりやすい名前をつけましょう。',
            placement: 'bottom' as const,
          },
          {
            target: '[data-tour="target-goal-type"]',
            content: '目標タイプを選択してください。減量、増量、維持など、あなたの目標に合わせて選択すると、最適なカロリー設定が計算されます。',
            placement: 'bottom' as const,
          },
          {
            target: '[data-tour="target-activity-level"]',
            content: '日常の活動レベルを選択してください。これに基づいて必要な総カロリーが計算されます。',
            placement: 'bottom' as const,
          },
          {
            target: '[data-tour="target-description"]',
            content: '具体的な目標を入力することで、AIがより個人に合った栄養プランを提案できます（任意）。',
            placement: 'top' as const,
          },
          {
            target: '[data-tour="target-submit"]',
            content: 'すべての情報を入力したら、ターゲットを生成してください。AIがあなた専用の栄養目標を計算します。',
            placement: 'top' as const,
          },
        ];

      case 'feature_calendar':
        return [
          {
            target: '[data-tour="calendar-header"]',
            content: 'カレンダー機能へようこそ！過去や未来の日付を選択して、食事記録を確認・編集できます。',
            placement: 'bottom' as const,
            disableBeacon: true,
          },
          {
            target: '[data-tour="calendar-main"]',
            content: 'カレンダーで任意の日付をクリックすると、その日の詳細を確認できます。色付きの日付は食事記録がある日を示しています。',
            placement: 'right' as const,
          },
          {
            target: '[data-tour="calendar-date-info"]',
            content: '選択した日付の概要情報が表示されます。食事記録の有無、目標達成度、AIレポートの状況を一目で確認できます。',
            placement: 'top' as const,
          },
          {
            target: '[data-tour="calendar-detail-header"]',
            content: '選択日の詳細セクションです。ここにその日の食事記録、栄養分析、目標達成度が表示されます。',
            placement: 'left' as const,
          },
          {
            target: '[data-tour="daily-summary"]',
            content: 'Todayページと同じように、選択した日の栄養サマリーが表示されます。過去のデータも含めて分析できます。',
            placement: 'top' as const,
          },
        ];

      case 'feature_nutrition':
        return [
          {
            target: '[data-tour="daily-summary"]',
            content: '栄養分析機能へようこそ！ここでは日々の栄養状況を詳細に分析できます。まず本日のサマリーカードから始めましょう。',
            placement: 'bottom' as const,
            disableBeacon: true,
          },
          {
            target: '[data-tour="meal-list"]',
            content: '各食事の「分析」ボタンをクリックすると、その食事の詳細な栄養分析が表示されます。食事ごとの栄養バランスを確認できます。',
            placement: 'top' as const,
          },
          {
            target: '[data-tour="target-progress"]',
            content: '目標達成度チャートです。主要栄養素、ミネラル、ビタミンなどの摂取状況を視覚的に確認できます。',
            placement: 'top' as const,
          },
          {
            target: '[data-tour="daily-report"]',
            content: 'AI生成の日次レポートで、栄養バランスや改善点についてのアドバイスが得られます。「レポートを生成する」ボタンで分析を開始できます。',
            placement: 'top' as const,
          },
        ];

      default:
        return [
          {
            target: 'body',
            content: 'チュートリアルシステムが正常に動作しています！',
            placement: 'center' as const,
            disableBeacon: true,
          },
        ];
    }
  };

  // 現在実行中のチュートリアルのステップを取得
  const tutorialSteps = runningTutorial ? getTutorialSteps(runningTutorial) : [];

  /**
   * Joyrideコールバック - チュートリアル進行を管理
   */
  const handleJoyrideCallback = useCallback(
    (data: CallBackProps) => {
      const { status, type, index, lifecycle } = data;

      // チュートリアル完了時の処理
      if (status === STATUS.FINISHED || status === STATUS.SKIPPED) {
        setIsRunning(false);

        // 初回完了のみ記録（統計用途）
        if (runningTutorial && status === STATUS.FINISHED && isMounted) {
          // 既に完了済みの場合は記録しない（重複防止）
          if (!tutorialModel.isTutorialCompleted(runningTutorial)) {
            console.log(`初回完了記録: ${runningTutorial}`);
            tutorialModel.markAsCompleted(runningTutorial);
          } else {
            console.log(`ヘルプ表示完了: ${runningTutorial} (記録済みのため送信しない)`);
          }
        }

        setRunningTutorial(null);
      }
    },
    [runningTutorial, isMounted, tutorialModel]
  );

  /**
   * チュートリアル開始 (外部から呼び出し可能)
   */
  const startTutorial = useCallback(
    (tutorialId: TutorialId) => {
      if (!isMounted || tutorialModel.isLoading) return;

      // ヘルプシステムとして完了状態に関係なく実行
      console.log(`ヘルプ "${tutorialId}" を表示中...`);
      setRunningTutorial(tutorialId);
      setIsRunning(true);
    },
    [isMounted, tutorialModel]
  );

  // TutorialProvider Context
  const tutorialContextValue = {
    startTutorial,
    runningTutorial,
    isRunning,
    isTutorialCompleted: isMounted ? tutorialModel.isTutorialCompleted : () => false,
  };

  // Hydration対策: クライアントサイドでのみJoyrideを表示
  if (!isMounted) {
    return (
      <TutorialContext.Provider value={tutorialContextValue}>
        {children}
      </TutorialContext.Provider>
    );
  }

  return (
    <TutorialContext.Provider value={tutorialContextValue}>
      {children}

      {/* react-joyride コンポーネント */}
      <Joyride
        steps={tutorialSteps}
        run={isRunning}
        continuous={true}
        showProgress={true}
        showSkipButton={true}
        callback={handleJoyrideCallback}
        styles={{
          options: {
            primaryColor: '#3b82f6', // blue-500
            textColor: '#374151', // gray-700
            backgroundColor: '#ffffff',
            arrowColor: '#ffffff',
            zIndex: 10000,
          },
          tooltip: {
            fontSize: '14px',
            fontFamily: 'inherit',
          },
          buttonNext: {
            backgroundColor: '#3b82f6',
            fontSize: '14px',
            padding: '8px 16px',
          },
          buttonBack: {
            color: '#6b7280',
            fontSize: '14px',
            padding: '8px 16px',
          },
          buttonSkip: {
            color: '#9ca3af',
            fontSize: '12px',
          },
        }}
        locale={{
          back: '戻る',
          close: '閉じる',
          last: '完了',
          next: '次へ',
          open: 'ダイアログを開く',
          skip: 'スキップ',
        }}
      />

      {/* デバッグ用: ステータス表示 (開発時のみ) */}
      {process.env.NODE_ENV === 'development' && (
        <div
          style={{
            position: 'fixed',
            bottom: '10px',
            left: '10px',
            background: '#000',
            color: '#fff',
            padding: '8px',
            fontSize: '12px',
            borderRadius: '4px',
            zIndex: 9999,
            opacity: isRunning ? 1 : 0.3,
          }}
        >
          Tutorial: {runningTutorial || 'None'} | Running: {isRunning ? 'Yes' : 'No'}
        </div>
      )}
    </TutorialContext.Provider>
  );
}

// Context (Step 8で完全実装予定)
export const TutorialContext = React.createContext<{
  startTutorial: (tutorialId: TutorialId) => void;
  runningTutorial: TutorialId | null;
  isRunning: boolean;
  isTutorialCompleted: (tutorialId: TutorialId) => boolean;
} | null>(null);

export function useTutorial() {
  const context = React.useContext(TutorialContext);
  if (!context) {
    throw new Error('useTutorial must be used within a TutorialProvider');
  }
  return context;
}