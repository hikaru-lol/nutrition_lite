/**
 * TodayPageContext - 状態管理の中央集権化
 *
 * 各ドメインフックを統合し、Context経由でコンポーネント間の状態を共有
 * プロップスドリリングを回避し、型安全な状態アクセスを提供
 */

'use client';

import { createContext, useContext, type ReactNode } from 'react';
import type { TodayPageContextValue } from '../types/todayTypes';
import { useTodayPageData, validateTodayPageData } from '../model/useTodayPageData';

// ========================================
// Context定義
// ========================================

export const TodayPageContext = createContext<TodayPageContextValue | null>(null);

// ========================================
// Context Hook
// ========================================

/**
 * TodayPageContextを使用するためのカスタムフック
 *
 * Provider外での使用を検出してエラーをスロー
 */
export function useTodayPageContext(): TodayPageContextValue {
  const context = useContext(TodayPageContext);
  if (!context) {
    throw new Error(
      'useTodayPageContext must be used within TodayPageProvider. ' +
      'Make sure to wrap your component with <TodayPageProvider>.'
    );
  }
  return context;
}

// ========================================
// Provider Props
// ========================================

interface TodayPageProviderProps {
  children: ReactNode;
  date: string;
}

// ========================================
// Provider Component (仮実装)
// ========================================

/**
 * TodayPageProvider - 状態提供コンポーネント
 *
 * useTodayPageDataフックと統合した完全実装
 */
export function TodayPageProvider({ children, date }: TodayPageProviderProps) {
  // 統合データフックから全ての状態を取得
  const contextValue = useTodayPageData({ date });

  // 開発時のデバッグ情報
  if (process.env.NODE_ENV === 'development') {
    const validation = validateTodayPageData(contextValue);
    if (validation.errors.length > 0) {
      console.error('TodayPageProvider validation errors:', validation.errors);
    }
    if (validation.warnings.length > 0) {
      console.warn('TodayPageProvider validation warnings:', validation.warnings);
    }
  }

  return (
    <TodayPageContext.Provider value={contextValue}>
      {children}
    </TodayPageContext.Provider>
  );
}

// ========================================
// 個別ドメインHook (convenience hooks)
// ========================================

/**
 * 食事データのみを取得するconvenience hook
 */
export function useTodayMeals() {
  const { meals } = useTodayPageContext();
  return meals;
}

/**
 * 目標データのみを取得するconvenience hook
 */
export function useTodayTargets() {
  const { targets } = useTodayPageContext();
  return targets;
}

/**
 * 栄養データのみを取得するconvenience hook
 */
export function useTodayNutrition() {
  const { nutrition } = useTodayPageContext();
  return nutrition;
}

/**
 * レポートデータのみを取得するconvenience hook
 */
export function useTodayReports() {
  const { reports } = useTodayPageContext();
  return reports;
}

/**
 * プロフィールデータのみを取得するconvenience hook
 */
export function useTodayProfile() {
  const { profile } = useTodayPageContext();
  return profile;
}

/**
 * モーダル状態のみを取得するconvenience hook
 */
export function useTodayModals() {
  const { modals } = useTodayPageContext();
  return modals;
}