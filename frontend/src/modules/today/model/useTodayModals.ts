/**
 * useTodayModals - モーダル管理専用フック
 *
 * 責務:
 * - 全モーダルの開閉状態管理
 * - モーダル間のデータ受け渡し
 * - モーダルの状態リセット
 */

'use client';

import { useState, useCallback } from 'react';

import type {
  TodayModalsModel,
  AddModalState,
  EditModalState,
  NutritionModalState,
  RecommendationModalState,
} from '../types/todayTypes';
import type { MealItemResponse } from '@/modules/meal/contract/mealContract';

// ========================================
// Initial States
// ========================================

const initialAddModalState: AddModalState = {
  isOpen: false,
  selectedMealType: 'main',
  selectedMealIndex: 1,
};

const initialEditModalState: EditModalState = {
  isOpen: false,
  editingMealItem: null,
};

const initialNutritionModalState: NutritionModalState = {
  isOpen: false,
  data: null,
};

const initialRecommendationModalState: RecommendationModalState = {
  isOpen: false,
  recommendation: null,
};

// ========================================
// Main Hook
// ========================================

export function useTodayModals(): TodayModalsModel {
  // ========================================
  // Modal States
  // ========================================

  const [addModal, setAddModal] = useState<AddModalState>(initialAddModalState);
  const [editModal, setEditModal] = useState<EditModalState>(initialEditModalState);
  const [nutritionModal, setNutritionModal] = useState<NutritionModalState>(initialNutritionModalState);
  const [recommendationModal, setRecommendationModal] = useState<RecommendationModalState>(initialRecommendationModalState);

  // ========================================
  // Add Modal Actions
  // ========================================

  const openAddModal = useCallback((mealType: 'main' | 'snack', mealIndex?: number) => {
    setAddModal({
      isOpen: true,
      selectedMealType: mealType,
      selectedMealIndex: mealType === 'main' ? (mealIndex ?? 1) : 1,
    });
  }, []);

  const closeAddModal = useCallback(() => {
    setAddModal(initialAddModalState);
  }, []);

  // ========================================
  // Edit Modal Actions
  // ========================================

  const openEditModal = useCallback((mealItem: MealItemResponse) => {
    setEditModal({
      isOpen: true,
      editingMealItem: {
        id: mealItem.id,
        date: mealItem.date,
        meal_type: mealItem.meal_type,
        meal_index: mealItem.meal_index,
        name: mealItem.name,
        amount_value: mealItem.amount_value,
        amount_unit: mealItem.amount_unit,
        serving_count: mealItem.serving_count,
        note: mealItem.note,
      },
    });
  }, []);

  const closeEditModal = useCallback(() => {
    setEditModal(initialEditModalState);
  }, []);

  // ========================================
  // Nutrition Modal Actions
  // ========================================

  const openNutritionModal = useCallback((data: any) => {
    setNutritionModal({
      isOpen: true,
      data,
    });
  }, []);

  const closeNutritionModal = useCallback(() => {
    setNutritionModal(initialNutritionModalState);
  }, []);

  // ========================================
  // Recommendation Modal Actions
  // ========================================

  const openRecommendationModal = useCallback(() => {
    // Note: 実際の推奨データは Context 経由で取得
    setRecommendationModal({
      isOpen: true,
      recommendation: null, // Context から取得される
    });
  }, []);

  const closeRecommendationModal = useCallback(() => {
    setRecommendationModal(initialRecommendationModalState);
  }, []);

  // ========================================
  // Utility Actions
  // ========================================

  /**
   * 全モーダルを閉じる
   */
  const closeAllModals = useCallback(() => {
    setAddModal(initialAddModalState);
    setEditModal(initialEditModalState);
    setNutritionModal(initialNutritionModalState);
    setRecommendationModal(initialRecommendationModalState);
  }, []);

  /**
   * モーダルが開いているかどうかを判定
   */
  const hasOpenModal = () => {
    return addModal.isOpen ||
           editModal.isOpen ||
           nutritionModal.isOpen ||
           recommendationModal.isOpen;
  };

  // ========================================
  // Return Value
  // ========================================

  return {
    // Modal States
    addModal,
    editModal,
    nutritionModal,
    recommendationModal,

    // Actions
    openAddModal,
    closeAddModal,
    openEditModal,
    closeEditModal,
    openNutritionModal,
    closeNutritionModal,
    openRecommendationModal,
    closeRecommendationModal,

    // Utility
    closeAllModals,
    hasOpenModal,
  };
}

// ========================================
// Specialized Hooks
// ========================================

/**
 * 特定のモーダルのみを管理する軽量フック
 */
export function useAddMealModal() {
  const [modalState, setModalState] = useState<AddModalState>(initialAddModalState);

  const open = useCallback((mealType: 'main' | 'snack', mealIndex?: number) => {
    setModalState({
      isOpen: true,
      selectedMealType: mealType,
      selectedMealIndex: mealType === 'main' ? (mealIndex ?? 1) : 1,
    });
  }, []);

  const close = useCallback(() => {
    setModalState(initialAddModalState);
  }, []);

  return {
    state: modalState,
    open,
    close,
  };
}

/**
 * 編集モーダル専用フック
 */
export function useEditMealModal() {
  const [modalState, setModalState] = useState<EditModalState>(initialEditModalState);

  const open = useCallback((mealItem: MealItemResponse) => {
    setModalState({
      isOpen: true,
      editingMealItem: {
        id: mealItem.id,
        date: mealItem.date,
        meal_type: mealItem.meal_type,
        meal_index: mealItem.meal_index,
        name: mealItem.name,
        amount_value: mealItem.amount_value,
        amount_unit: mealItem.amount_unit,
        serving_count: mealItem.serving_count,
        note: mealItem.note,
      },
    });
  }, []);

  const close = useCallback(() => {
    setModalState(initialEditModalState);
  }, []);

  return {
    state: modalState,
    open,
    close,
  };
}

// ========================================
// Modal Event Handlers
// ========================================

/**
 * キーボードイベント処理（ESCキーでモーダルを閉じる）
 */
export function useModalKeyboardHandler(modals: TodayModalsModel) {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.key === 'Escape' && modals.hasOpenModal()) {
      event.preventDefault();
      modals.closeAllModals();
    }
  }, [modals]);

  return handleKeyDown;
}

/**
 * モーダル外クリック処理
 */
export function useModalOutsideClick(
  isOpen: boolean,
  onClose: () => void,
  ref: React.RefObject<HTMLElement>
) {
  const handleOutsideClick = useCallback((event: MouseEvent) => {
    if (isOpen && ref.current && !ref.current.contains(event.target as Node)) {
      onClose();
    }
  }, [isOpen, onClose, ref]);

  return handleOutsideClick;
}

// ========================================
// Modal State Helpers
// ========================================

/**
 * モーダルのZ-index管理
 */
export function getModalZIndex(modalType: 'add' | 'edit' | 'nutrition' | 'recommendation'): number {
  const zIndexMap = {
    add: 50,
    edit: 51,
    nutrition: 52,
    recommendation: 53,
  };
  return zIndexMap[modalType];
}

/**
 * モーダルのアクセシビリティ属性を生成
 */
export function getModalA11yProps(modalId: string, titleId: string, isOpen: boolean) {
  return {
    'aria-modal': isOpen,
    'aria-labelledby': titleId,
    'id': modalId,
    'role': 'dialog',
    'aria-hidden': !isOpen,
  };
}