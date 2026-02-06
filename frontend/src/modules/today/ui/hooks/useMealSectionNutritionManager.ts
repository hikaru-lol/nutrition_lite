/**
 * useMealSectionNutritionManager - Layer 2: UI Orchestration
 *
 * 責務:
 * - 食事セクション毎の栄養データキャッシュ管理
 * - 栄養分析のfetch/cache/UIロジック
 * - 複雑な表示用データ変換
 *
 * 移行元: useTodayPageModel.ts の以下の機能
 * - fetchMealNutrition function
 * - getMealNutritionFromCache function
 * - getMealSectionKey function
 * - nutritionCheckState management
 */

'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import {
  computeNutritionData,
  getNutritionData,
} from '@/modules/nutrition/api/nutritionClient';
import type { MealType } from '@/modules/meal/contract/mealContract';

// ========================================
// Types
// ========================================

export interface MealSectionNutritionManager {
  // キャッシュ管理
  fetchMealNutrition: (meal_type: MealType, meal_index?: number) => Promise<any>;
  getMealNutritionFromCache: (meal_type: MealType, meal_index?: number) => any;
  getMealSectionKey: (meal_type: MealType, meal_index?: number) => string;

  // 栄養チェック状態管理
  nutritionCheckState: Record<string, boolean>;

  // ヘルパー
  isNutritionDataLoading: (meal_type: MealType, meal_index?: number) => boolean;
}

// ========================================
// Hook Implementation
// ========================================

interface UseMealSectionNutritionManagerProps {
  date: string;
  mealItems?: readonly any[]; // 食事アイテムリスト
}

export function useMealSectionNutritionManager({
  date,
  mealItems = [],
}: UseMealSectionNutritionManagerProps): MealSectionNutritionManager {
  const queryClient = useQueryClient();

  // ========================================
  // State
  // ========================================

  const [nutritionCheckState, setNutritionCheckState] = useState<Record<string, boolean>>({});

  // ========================================
  // Helper Functions
  // ========================================

  // 食事セクション毎のキー生成
  const getMealSectionKey = useCallback((meal_type: MealType, meal_index?: number) => {
    return `${meal_type}${meal_index ? `-${meal_index}` : ''}`;
  }, []);

  // 食事アイテムから食事セクションのリストを生成
  const getMealSections = useCallback((mealItems: readonly any[]) => {
    const sections = new Set<string>();
    const result: { mealType: MealType; mealIndex?: number }[] = [];

    mealItems.forEach(item => {
      const key = item.meal_type === 'main'
        ? `${item.meal_type}-${item.meal_index}`
        : item.meal_type;

      if (!sections.has(key)) {
        sections.add(key);
        result.push({
          mealType: item.meal_type,
          mealIndex: item.meal_type === 'main' ? item.meal_index : undefined
        });
      }
    });

    return result;
  }, []);

  // 栄養データ存在確認（軽量版）
  const checkNutritionDataExists = useCallback(async (meal_type: MealType, meal_index?: number) => {
    try {
      const data = await getNutritionData({
        date,
        meal_type,
        meal_index: meal_index ?? null,
      });

      // データが取得できた場合はキャッシュに保存
      const queryKey = [
        'nutrition',
        'meal-section',
        date,
        meal_type,
        meal_index ?? null
      ] as const;
      queryClient.setQueryData(queryKey, data);
      return true;
    } catch (error) {
      return false;
    }
  }, [date, queryClient]);

  // ========================================
  // Main Functions
  // ========================================

  // 食事セクションの栄養データを手動で取得
  const fetchMealNutrition = useCallback(async (meal_type: MealType, meal_index?: number) => {
    const queryKey = [
      'nutrition',
      'meal-section',
      date,
      meal_type,
      meal_index ?? null
    ] as const;

    // 既にキャッシュにデータがある場合は再取得しない
    const existingData = queryClient.getQueryData(queryKey);
    if (existingData) {
      return existingData;
    }

    // データを取得してキャッシュに保存
    const data = await queryClient.fetchQuery({
      queryKey,
      queryFn: () => computeNutritionData({
        date,
        meal_type,
        meal_index: meal_index ?? null,
      }),
      staleTime: 1000 * 60 * 30,
    });

    return data;
  }, [date, queryClient]);

  // 食事セクションの栄養データがキャッシュに存在するかチェック
  const getMealNutritionFromCache = useCallback((meal_type: MealType, meal_index?: number) => {
    const sectionKey = `${meal_type}-${meal_index ?? 'null'}`;
    const queryKey = [
      'nutrition',
      'meal-section',
      date,
      meal_type,
      meal_index ?? null
    ] as const;

    // まずメインの栄養データキャッシュを確認
    const nutritionData = queryClient.getQueryData(queryKey);
    if (nutritionData) {
      return nutritionData;
    }

    // 存在チェック状態も確認
    const checkExists = nutritionCheckState[sectionKey];
    if (checkExists === true) {
      // データが存在することは確認されているが、まだキャッシュにない
      return { exists: true, loading: true };
    } else if (checkExists === false) {
      // データが存在しないことが確認済み
      return null;
    }

    // まだチェック中
    return { loading: true };
  }, [date, queryClient, nutritionCheckState]);

  // ローディング状態確認
  const isNutritionDataLoading = useCallback((meal_type: MealType, meal_index?: number) => {
    const sectionKey = getMealSectionKey(meal_type, meal_index);
    const checkState = nutritionCheckState[sectionKey];
    return checkState === undefined; // チェック中
  }, [getMealSectionKey, nutritionCheckState]);

  // ========================================
  // Effects
  // ========================================

  // 食事セクションリスト生成
  const mealSections = useMemo(() => {
    if (!mealItems) return [];
    return getMealSections(mealItems);
  }, [mealItems, getMealSections]);

  // 各食事セクションの栄養データ存在確認を自動実行
  useEffect(() => {
    const checkAllMealSections = async () => {
      if (mealSections.length > 0) {
        // 各食事セクションの栄養データが存在するかチェックして存在フラグをキャッシュに保存
        const checkPromises = mealSections.map(async ({ mealType, mealIndex }) => {
          const sectionKey = getMealSectionKey(mealType, mealIndex);
          const existsQueryKey = [
            'nutrition',
            'exists',
            date,
            mealType,
            mealIndex ?? null
          ] as const;

          // 既にチェック済みならスキップ
          const existingCheck = queryClient.getQueryData(existsQueryKey);
          if (existingCheck !== undefined) {
            setNutritionCheckState(prev => ({ ...prev, [sectionKey]: existingCheck as boolean }));
            return;
          }

          // 存在確認を実行してキャッシュに保存
          try {
            const exists = await checkNutritionDataExists(mealType, mealIndex);
            queryClient.setQueryData(existsQueryKey, exists);
            setNutritionCheckState(prev => ({ ...prev, [sectionKey]: exists }));
          } catch (error) {
            queryClient.setQueryData(existsQueryKey, false);
            setNutritionCheckState(prev => ({ ...prev, [sectionKey]: false }));
          }
        });

        // 全ての確認が完了するまで待つ
        await Promise.all(checkPromises);
      }
    };

    checkAllMealSections();
  }, [mealSections, date, queryClient, getMealSectionKey, checkNutritionDataExists]);

  // ========================================
  // Return Model
  // ========================================

  return {
    // Cache Management
    fetchMealNutrition,
    getMealNutritionFromCache,
    getMealSectionKey,

    // State
    nutritionCheckState,

    // Helpers
    isNutritionDataLoading,
  };
}