/**
 * useNutritionAnalysisModalState - Layer 2: UI Orchestration
 *
 * 責務:
 * - 栄養分析詳細モーダルの状態管理
 * - モーダルの開閉制御
 * - 栄養データの管理とデータ変換
 */

'use client';

import { useState, useCallback } from 'react';
import type { NutritionDetailsData } from '@/modules/nutrition/types/nutritionTypes';

// ========================================
// Types
// ========================================

export interface NutritionAnalysisModalState {
  isOpen: boolean;
  nutritionDetailsData: any | null;
  typedNutritionData: NutritionDetailsData | null;
}

export interface NutritionAnalysisModalActions {
  open: (nutritionData: any) => void;
  close: () => void;
}

export interface NutritionAnalysisModalModel extends NutritionAnalysisModalState, NutritionAnalysisModalActions {}

// ========================================
// Hook Implementation
// ========================================

export function useNutritionAnalysisModalState(): NutritionAnalysisModalModel {
  // ========================================
  // State
  // ========================================

  const [isOpen, setIsOpen] = useState(false);
  const [nutritionDetailsData, setNutritionDetailsData] = useState<any | null>(null);
  const [typedNutritionData, setTypedNutritionData] = useState<NutritionDetailsData | null>(null);

  // ========================================
  // Actions
  // ========================================

  const open = useCallback((nutritionData: any) => {
    // === 既存データ形式での保存（後方互換性のため） ===
    setNutritionDetailsData(nutritionData);

    // === 新規型定義への変換 ===
    try {
      const typedData: NutritionDetailsData = {
        meal: nutritionData.meal || {
          id: nutritionData.id || 'unknown',
          name: nutritionData.name || '不明な食事',
          meal_type: nutritionData.meal_type || 'main',
          meal_index: nutritionData.meal_index || 1,
          totalCalories: nutritionData.totalCalories || 0,
          nutrients: nutritionData.nutrients || []
        },
        daily: nutritionData.daily || {
          date: nutritionData.date || new Date().toISOString().slice(0, 10),
          totalCalories: nutritionData.totalCalories || 0,
          nutrients: nutritionData.nutrients || [],
          mealCount: 1
        }
      };

      setTypedNutritionData(typedData);
    } catch (error) {
      console.error('栄養データ変換エラー:', error);
      setTypedNutritionData(null);
    }

    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
    setNutritionDetailsData(null);
    setTypedNutritionData(null);
  }, []);

  // ========================================
  // Return Model
  // ========================================

  return {
    // State
    isOpen,
    nutritionDetailsData,
    typedNutritionData,

    // Actions
    open,
    close,
  };
}