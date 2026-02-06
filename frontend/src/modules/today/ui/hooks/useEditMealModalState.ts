/**
 * useEditMealModalState - Layer 2: UI Orchestration
 *
 * 責務:
 * - 食事編集モーダルの状態管理
 * - モーダルの開閉制御
 * - 編集対象アイテムの管理
 */

'use client';

import { useState, useCallback } from 'react';
import type { MealItem } from '@/modules/meal/contract/mealContract';
import type { MealItemForEdit } from '../components/EditMealModal';

// ========================================
// Types
// ========================================

export interface EditMealModalState {
  isOpen: boolean;
  editingMealItem: MealItemForEdit | null;
}

export interface EditMealModalActions {
  open: (mealItem: MealItem, date: string) => void;
  close: () => void;
}

export interface EditMealModalModel extends EditMealModalState, EditMealModalActions {}

// ========================================
// Hook Implementation
// ========================================

export function useEditMealModalState(): EditMealModalModel {
  // ========================================
  // State
  // ========================================

  const [isOpen, setIsOpen] = useState(false);
  const [editingMealItem, setEditingMealItem] = useState<MealItemForEdit | null>(null);

  // ========================================
  // Actions
  // ========================================

  const open = useCallback((mealItem: MealItem, date: string) => {
    setEditingMealItem({
      id: mealItem.id,
      date: date,
      meal_type: mealItem.meal_type,
      meal_index: mealItem.meal_index ?? null,
      name: mealItem.name,
      serving_count: mealItem.serving_count ?? null,
      note: mealItem.note ?? null,
    });
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
    setEditingMealItem(null);
  }, []);

  // ========================================
  // Return Model
  // ========================================

  return {
    // State
    isOpen,
    editingMealItem,

    // Actions
    open,
    close,
  };
}