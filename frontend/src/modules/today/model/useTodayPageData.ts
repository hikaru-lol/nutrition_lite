/**
 * useTodayPageData - 統合データ管理フック
 *
 * 責務:
 * - 全ドメインフックの統合
 * - ドメイン間の依存関係管理
 * - Context用のデータ提供
 */

'use client';

import { useMemo } from 'react';
import type { TodayPageContextValue } from '../types/todayTypes';
import { formatLocalDateYYYYMMDD } from '../types/todayTypes';
import { useTodayMeals } from './useTodayMeals';
import { useTodayTargets } from './useTodayTargets';
import { useTodayNutrition } from './useTodayNutrition';
import { useTodayReports } from './useTodayReports';
import { useTodayProfile } from './useTodayProfile';
import { useTodayModals } from './useTodayModals';

// ========================================
// Props Interface
// ========================================

interface UseTodayPageDataProps {
  date?: string; // YYYY-MM-DD format
}

// ========================================
// Main Hook
// ========================================

export function useTodayPageData(props: UseTodayPageDataProps = {}): TodayPageContextValue {
  // 日付の正規化
  const date = useMemo(() => {
    return props.date || formatLocalDateYYYYMMDD(new Date());
  }, [props.date]);

  // ========================================
  // Domain Hooks Integration
  // ========================================

  // 各ドメインフックを実行（依存関係を考慮した順序）
  const profile = useTodayProfile();
  const meals = useTodayMeals({ date });
  const targets = useTodayTargets({ date });

  // 栄養分析フック（食事データに依存）
  const nutrition = useTodayNutrition({ date });

  // レポートフック（食事データと設定に依存）
  const reports = useTodayReports({
    date,
    mealItemsCount: meals.items.length,
    mealsPerDay: profile.mealsPerDay,
  });

  // モーダル管理フック（依存関係なし）
  const modals = useTodayModals();

  // ========================================
  // Cross-Domain Integration
  // ========================================

  // 栄養詳細表示のモーダル連携
  const enhancedNutrition = useMemo(() => {
    return {
      ...nutrition,
      showDetails: (data: any) => {
        modals.openNutritionModal(data);
      },
    };
  }, [nutrition, modals.openNutritionModal]);

  // 食事推奨モーダル連携
  const enhancedModals = useMemo(() => {
    return {
      ...modals,
      openRecommendationModal: () => {
        // 実際の推奨データを取得してモーダルを開く
        // ここでは簡略化
        modals.openRecommendationModal();
      },
    };
  }, [modals]);

  // ========================================
  // Global State Computation
  // ========================================

  // 統合ローディング状態
  const isLoading = useMemo(() => {
    return meals.isLoading ||
           targets.isLoading ||
           profile.isLoading ||
           reports.isLoading;
  }, [meals.isLoading, targets.isLoading, profile.isLoading, reports.isLoading]);

  // 統合エラー状態
  const hasError = useMemo(() => {
    return meals.isError ||
           targets.isError ||
           profile.isError ||
           reports.isError;
  }, [meals.isError, targets.isError, profile.isError, reports.isError]);

  // ========================================
  // Return Value
  // ========================================

  return {
    // メタデータ
    date,

    // ドメインモデル
    meals,
    targets,
    nutrition: enhancedNutrition,
    reports,
    profile,
    modals: enhancedModals,

    // 統合状態
    isLoading,
    hasError,
  };
}

// ========================================
// 軽量版Hook（特定ドメインのみ）
// ========================================

/**
 * 食事管理のみに特化した軽量データフック
 */
export function useTodayMealPageData(props: UseTodayPageDataProps = {}) {
  const date = useMemo(() => {
    return props.date || formatLocalDateYYYYMMDD(new Date());
  }, [props.date]);

  const meals = useTodayMeals({ date });
  const modals = useTodayModals();

  return {
    date,
    meals,
    modals,
    isLoading: meals.isLoading,
    hasError: meals.isError,
  };
}

/**
 * 栄養分析のみに特化した軽量データフック
 */
export function useTodayNutritionPageData(props: UseTodayPageDataProps = {}) {
  const date = useMemo(() => {
    return props.date || formatLocalDateYYYYMMDD(new Date());
  }, [props.date]);

  const meals = useTodayMeals({ date });
  const targets = useTodayTargets({ date });
  const nutrition = useTodayNutrition({ date });

  return {
    date,
    meals,
    targets,
    nutrition,
    isLoading: meals.isLoading || targets.isLoading,
    hasError: meals.isError || targets.isError,
  };
}

// ========================================
// Data Validation Helpers
// ========================================

/**
 * データ整合性チェック
 */
export function validateTodayPageData(data: TodayPageContextValue): {
  isValid: boolean;
  errors: string[];
  warnings: string[];
} {
  const errors: string[] = [];
  const warnings: string[] = [];

  // 必須データの存在確認
  if (!data.date) {
    errors.push('日付が設定されていません');
  }

  // プロフィール設定の確認
  if (!data.profile.profile) {
    warnings.push('プロフィールが未設定です');
  }

  // 目標設定の確認
  if (!data.targets.activeTarget) {
    warnings.push('栄養目標が設定されていません');
  }

  // データの依存関係確認
  if (data.meals.items.length > 0 && !data.targets.activeTarget) {
    warnings.push('食事データがありますが目標が設定されていません');
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
  };
}

/**
 * パフォーマンス監視
 */
export function useTodayPagePerformance(data: TodayPageContextValue) {
  return useMemo(() => {
    const metrics = {
      mealItemsCount: data.meals.items.length,
      nutritionCacheSize: data.nutrition.nutritionCache.size,
      isLoading: data.isLoading,
      hasError: data.hasError,
      timestamp: Date.now(),
    };

    // 開発時のパフォーマンス警告
    if (process.env.NODE_ENV === 'development') {
      if (metrics.mealItemsCount > 20) {
        console.warn('TodayPage: 食事アイテム数が多すぎます', metrics.mealItemsCount);
      }
      if (metrics.nutritionCacheSize > 10) {
        console.warn('TodayPage: 栄養キャッシュサイズが大きすぎます', metrics.nutritionCacheSize);
      }
    }

    return metrics;
  }, [data.meals.items.length, data.nutrition.nutritionCache.size, data.isLoading, data.hasError]);
}