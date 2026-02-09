/**
 * チュートリアル手動起動ボタン（ヘルプシステム）
 */

'use client';

import React from 'react';
import type { TutorialId } from '../contract/tutorialContract';
import { useTutorial } from './TutorialProvider';

interface TutorialTriggerProps {
  tutorialId: TutorialId;
  children?: React.ReactNode;
  className?: string;
  disabled?: boolean;
  onStart?: () => void;
}

export function TutorialTrigger({
  tutorialId,
  children = '？',
  className = '',
  disabled = false,
  onStart,
}: TutorialTriggerProps) {
  const { startTutorial } = useTutorial();

  const handleClick = () => {
    if (disabled) return;

    onStart?.();
    startTutorial(tutorialId);
    console.log(`ヘルプ "${tutorialId}" を表示`);
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled}
      className={`
        inline-flex items-center justify-center
        w-6 h-6 rounded-full text-xs font-medium
        transition-colors duration-200 hover:scale-105
        bg-blue-100 text-blue-700 hover:bg-blue-200
        dark:bg-blue-900/20 dark:text-blue-300 dark:hover:bg-blue-900/40
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${className}
      `}
      title={`ヘルプ "${tutorialId}" を表示`}
    >
      {children}
    </button>
  );
}