'use client';

import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  fullScreen?: boolean;
}

export function LoadingState({
  label = 'データを読み込み中...',
  size = 'md',
  fullScreen = false
}: LoadingStateProps) {
  // サイズ設定
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  const textSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  };

  // フルスクリーン表示
  if (fullScreen) {
    return (
      <div
        className="fixed inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm z-50"
        role="status"
        aria-live="polite"
        aria-label={label}
      >
        <div className="flex flex-col items-center gap-4">
          <Loader2
            className={`${sizeClasses[size]} text-primary animate-spin`}
            aria-hidden="true"
          />
          <p className={`${textSizeClasses[size]} text-muted-foreground font-medium animate-pulse`}>
            {label}
          </p>
        </div>
      </div>
    );
  }

  // 通常表示
  return (
    <div
      className="w-full rounded-xl border bg-card p-8 flex flex-col items-center justify-center gap-4"
      role="status"
      aria-live="polite"
      aria-label={label}
    >
      <div className="relative">
        {/* 背景のパルス効果 */}
        <div className="absolute inset-0 rounded-full bg-primary/10 animate-ping" />

        {/* スピナー */}
        <Loader2
          className={`${sizeClasses[size]} text-primary animate-spin relative z-10`}
          aria-hidden="true"
        />
      </div>

      <p className={`${textSizeClasses[size]} text-muted-foreground font-medium`}>
        {label}
      </p>
    </div>
  );
}
