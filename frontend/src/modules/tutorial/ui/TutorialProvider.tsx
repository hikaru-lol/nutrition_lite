/**
 * チュートリアル機能のプロバイダーコンポーネント
 * react-joyrideの統合とヘルプシステム
 */

'use client';

import React, { useState, useCallback, useEffect } from 'react';
import Joyride, { CallBackProps, STATUS } from 'react-joyride';
import { getTutorialSteps } from '../contract/tutorialSteps';
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

  // 現在実行中のチュートリアルのステップを取得
  const tutorialSteps = runningTutorial ? getTutorialSteps(runningTutorial) : [];

  /**
   * Joyrideコールバック - チュートリアル進行を管理
   */
  const handleJoyrideCallback = useCallback(
    (data: CallBackProps) => {
      const { status, action } = data;

      // 終了条件：完了、スキップ、または明示的な終了アクション
      const shouldEnd =
        status === STATUS.FINISHED ||
        status === STATUS.SKIPPED ||
        action === 'close' ||
        action === 'skip' ||
        action === 'reset';

      if (shouldEnd) {
        setIsRunning(false);
        setRunningTutorial(null);
      }
    },
    []
  );

  /**
   * チュートリアル開始 (外部から呼び出し可能)
   */
  const startTutorial = useCallback(
    (tutorialId: TutorialId) => {
      if (!isMounted) return;

      console.log(`ヘルプ "${tutorialId}" を表示中...`);
      setRunningTutorial(tutorialId);
      setIsRunning(true);
    },
    [isMounted]
  );

  // TutorialProvider Context
  const tutorialContextValue = {
    startTutorial,
    runningTutorial,
    isRunning,
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
    </TutorialContext.Provider>
  );
}

/**
 * Tutorial Context - グローバルなチュートリアル機能へのアクセス
 */
export const TutorialContext = React.createContext<{
  startTutorial: (tutorialId: TutorialId) => void;
  runningTutorial: TutorialId | null;
  isRunning: boolean;
} | null>(null);

/**
 * useTutorial - チュートリアル機能にアクセスするためのカスタムフック
 *
 * @example
 * const { startTutorial } = useTutorial();
 * startTutorial('feature_today');
 */
export function useTutorial() {
  const context = React.useContext(TutorialContext);
  if (!context) {
    throw new Error('useTutorial must be used within a TutorialProvider');
  }
  return context;
}