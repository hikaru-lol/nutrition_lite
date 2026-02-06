/**
 * useMealRecommendationModalState - Layer 2: UI Orchestration
 *
 * 責務:
 * - 食事提案詳細モーダルの状態管理
 * - モーダルの開閉制御
 * - 提案データの管理
 */

'use client';

import { useState, useCallback } from 'react';

// ========================================
// Types
// ========================================

export interface MealRecommendationModalState {
  isOpen: boolean;
  selectedRecommendation: any | null;
}

export interface MealRecommendationModalActions {
  open: (recommendation: any) => void;
  close: () => void;
}

export interface MealRecommendationModalModel extends MealRecommendationModalState, MealRecommendationModalActions {}

// ========================================
// Hook Implementation
// ========================================

export function useMealRecommendationModalState(): MealRecommendationModalModel {
  // ========================================
  // State
  // ========================================

  const [isOpen, setIsOpen] = useState(false);
  const [selectedRecommendation, setSelectedRecommendation] = useState<any | null>(null);

  // ========================================
  // Actions
  // ========================================

  const open = useCallback((recommendation: any) => {
    setSelectedRecommendation(recommendation);
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
    setSelectedRecommendation(null);
  }, []);

  // ========================================
  // Return Model
  // ========================================

  return {
    // State
    isOpen,
    selectedRecommendation,

    // Actions
    open,
    close,
  };
}