/**
 * チュートリアル手動起動ボタン
 */

'use client';

import React from 'react';
import type { TutorialId } from '../contract/tutorialContract';
import { useTutorialModel } from '../model/useTutorialModel';
import { useTutorial } from './TutorialProvider';

interface TutorialTriggerProps {
  tutorialId: TutorialId;
  children?: React.ReactNode;
  className?: string;
  disabled?: boolean;
  onStart?: () => void; // Step 8で Context 統合予定
}

export function TutorialTrigger({
  tutorialId,
  children = '？',
  className = '',
  disabled = false,
  onStart,
}: TutorialTriggerProps) {
  const { isTutorialCompleted, isLoading } = useTutorialModel();
  const { startTutorial } = useTutorial();

  const isCompleted = isTutorialCompleted(tutorialId);
  const isDisabled = disabled || isLoading;

  const handleClick = () => {
    if (isDisabled) return;

    // ヘルプシステムとして起動（完了状態に関係なく実行）
    onStart?.();
    startTutorial(tutorialId);
    console.log(`ヘルプ "${tutorialId}" を表示`);
  };

  return (
    <button
      onClick={handleClick}
      disabled={isDisabled}
      className={`
        inline-flex items-center justify-center
        w-6 h-6 rounded-full text-xs font-medium
        transition-colors duration-200 hover:scale-105
        bg-blue-100 text-blue-700 hover:bg-blue-200
        dark:bg-blue-900/20 dark:text-blue-300 dark:hover:bg-blue-900/40
        ${isCompleted ? 'opacity-80' : ''}
        ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${className}
      `}
      title={`ヘルプ "${tutorialId}" を表示`}
    >
      ？
    </button>
  );
}