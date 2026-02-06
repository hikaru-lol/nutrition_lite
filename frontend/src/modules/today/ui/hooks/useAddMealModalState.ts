/**
 * useAddMealModalState - Layer 2: UI Orchestration
 *
 * 責務:
 * - 食事追加モーダルの状態管理
 * - モーダルの開閉制御
 * - フォームパラメータの管理
 */

'use client';

import { useState, useCallback } from 'react';

// ========================================
// Types
// ========================================

export interface AddMealModalState {
  isOpen: boolean;
  selectedMealType: 'main' | 'snack';
  selectedMealIndex: number;
}

export interface AddMealModalActions {
  open: (mealType: 'main' | 'snack', mealIndex?: number) => void;
  close: () => void;
}

export interface AddMealModalModel extends AddMealModalState, AddMealModalActions {}

// ========================================
// Hook Implementation
// ========================================

export function useAddMealModalState(): AddMealModalModel {
  // ========================================
  // State
  // ========================================

  const [isOpen, setIsOpen] = useState(false);
  const [selectedMealType, setSelectedMealType] = useState<'main' | 'snack'>('main');
  const [selectedMealIndex, setSelectedMealIndex] = useState(1);

  // ========================================
  // Actions
  // ========================================

  const open = useCallback((mealType: 'main' | 'snack', mealIndex?: number) => {
    setSelectedMealType(mealType);
    if (mealType === 'main' && mealIndex) {
      setSelectedMealIndex(mealIndex);
    }
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
  }, []);

  // ========================================
  // Return Model
  // ========================================

  return {
    // State
    isOpen,
    selectedMealType,
    selectedMealIndex,

    // Actions
    open,
    close,
  };
}