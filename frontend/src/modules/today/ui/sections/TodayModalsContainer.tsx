/**
 * TodayModalsContainer - モーダル統合管理セクション
 *
 * 責務:
 * - Context経由でのモーダル状態管理
 * - 全TodayPage関連モーダルの統合表示
 * - モーダル間の競合解決とアクセシビリティ
 */

'use client';

import { useEffect } from 'react';
import {
  useTodayModals,
  useTodayMeals,
  useTodayNutrition,
} from '../../context/TodayPageContext';

// ========================================
// Component Interface
// ========================================

interface TodayModalsContainerProps {
  className?: string;
  date: string;
}

// ========================================
// Main Component
// ========================================

export function TodayModalsContainer({
  className,
  date,
}: TodayModalsContainerProps) {
  // Context経由で各ドメインデータを取得
  const modals = useTodayModals();
  const meals = useTodayMeals();
  const nutrition = useTodayNutrition();

  // ========================================
  // Keyboard Accessibility
  // ========================================

  // Escapeキーでモーダル閉じる
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && modals.hasOpenModal()) {
        event.preventDefault();
        modals.closeAllModals();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [modals.hasOpenModal, modals.closeAllModals]);

  // ========================================
  // Modal Event Handlers
  // ========================================

  // 食事追加モーダルのハンドラー
  const handleAddMealSubmit = async (values: any) => {
    try {
      await meals.add({
        ...values,
        date,
        meal_type: modals.addModal.selectedMealType,
        meal_index: modals.addModal.selectedMealIndex,
      });
      modals.closeAddModal();
    } catch (error) {
      console.error('食事追加エラー:', error);
      // エラーはuseTodayMealsフック内でトースト表示される
    }
  };

  // 食事編集モーダルのハンドラー
  const handleEditMealSubmit = async (values: any) => {
    if (!modals.editModal.editingMealItem) return;

    try {
      await meals.update(modals.editModal.editingMealItem.id, {
        ...values,
        date,
      });
      modals.closeEditModal();
    } catch (error) {
      console.error('食事編集エラー:', error);
      // エラーはuseTodayMealsフック内でトースト表示される
    }
  };

  // 栄養分析モーダルのハンドラー
  const handleNutritionModalClose = () => {
    modals.closeNutritionModal();
    // 栄養分析の選択状態もクリア
    nutrition.clearSelected();
  };

  // 推奨モーダルのハンドラー
  const handleRecommendationAccept = async (recommendation: any) => {
    try {
      // 推奨内容を食事として追加
      await meals.add({
        ...recommendation,
        date,
        meal_type: 'main', // デフォルトで主食として追加
        meal_index: 1,
      });
      modals.closeRecommendationModal();
    } catch (error) {
      console.error('推奨受け入れエラー:', error);
    }
  };

  // ========================================
  // Render
  // ========================================

  return (
    <div className={className}>
      {/* モーダル統合コンテナ - 将来実装予定 */}

      {/* 食事追加モーダル - プレースホルダー */}
      {modals.addModal.isOpen && (
        <PlaceholderModal
          title="食事追加モーダル"
          onClose={modals.closeAddModal}
          isOpen={modals.addModal.isOpen}
        />
      )}

      {/* 食事編集モーダル - プレースホルダー */}
      {modals.editModal.isOpen && (
        <PlaceholderModal
          title="食事編集モーダル"
          onClose={modals.closeEditModal}
          isOpen={modals.editModal.isOpen}
        />
      )}

      {/* 栄養分析モーダル - プレースホルダー */}
      {modals.nutritionModal.isOpen && (
        <PlaceholderModal
          title="栄養分析モーダル"
          onClose={handleNutritionModalClose}
          isOpen={modals.nutritionModal.isOpen}
        />
      )}

      {/* 推奨モーダル - プレースホルダー */}
      {modals.recommendationModal.isOpen && (
        <PlaceholderModal
          title="推奨モーダル"
          onClose={modals.closeRecommendationModal}
          isOpen={modals.recommendationModal.isOpen}
        />
      )}
    </div>
  );
}

// ========================================
// 軽量版・特殊用途バリエーション
// ========================================

/**
 * 特定のモーダルのみを管理する軽量版
 */
interface SpecificModalContainerProps {
  className?: string;
  date: string;
  modalType: 'add' | 'edit' | 'nutrition' | 'recommendation';
}

export function SpecificModalContainer({
  className,
  date,
  modalType,
}: SpecificModalContainerProps) {
  const modals = useTodayModals();
  const meals = useTodayMeals();
  const nutrition = useTodayNutrition();

  // Event handlers (同じ実装)
  const handleAddMealSubmit = async (values: any) => {
    try {
      await meals.add({
        ...values,
        date,
        meal_type: modals.addModal.selectedMealType,
        meal_index: modals.addModal.selectedMealIndex,
      });
      modals.closeAddModal();
    } catch (error) {
      console.error('食事追加エラー:', error);
    }
  };

  const handleEditMealSubmit = async (values: any) => {
    if (!modals.editModal.editingMealItem) return;
    try {
      await meals.update(modals.editModal.editingMealItem.id, {
        ...values,
        date,
      });
      modals.closeEditModal();
    } catch (error) {
      console.error('食事編集エラー:', error);
    }
  };

  const handleNutritionModalClose = () => {
    modals.closeNutritionModal();
    nutrition.clearSelected();
  };

  const renderModal = () => {
    switch (modalType) {
      case 'add':
        return (
          <PlaceholderModal
            title="食事追加モーダル"
            onClose={modals.closeAddModal}
            isOpen={modals.addModal.isOpen}
          />
        );

      case 'edit':
        return (
          <PlaceholderModal
            title="食事編集モーダル"
            onClose={modals.closeEditModal}
            isOpen={modals.editModal.isOpen}
          />
        );

      case 'nutrition':
        return (
          <PlaceholderModal
            title="栄養分析モーダル"
            onClose={handleNutritionModalClose}
            isOpen={modals.nutritionModal.isOpen}
          />
        );

      case 'recommendation':
        return (
          <PlaceholderModal
            title="推奨モーダル"
            onClose={modals.closeRecommendationModal}
            isOpen={modals.recommendationModal.isOpen}
          />
        );

      default:
        return null;
    }
  };

  return <div className={className}>{renderModal()}</div>;
}

/**
 * モーダル状態インジケーター（開発・デバッグ用）
 */
export function ModalStatusIndicator({ className }: { className?: string }) {
  const modals = useTodayModals();

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  const getActiveModals = () => {
    const active = [];
    if (modals.addModal.isOpen) active.push('追加');
    if (modals.editModal.isOpen) active.push('編集');
    if (modals.nutritionModal.isOpen) active.push('栄養分析');
    if (modals.recommendationModal.isOpen) active.push('推奨');
    return active;
  };

  const activeModals = getActiveModals();

  return (
    <div className={`fixed bottom-4 right-4 z-50 ${className}`}>
      <div className="bg-black/80 text-white text-xs p-2 rounded max-w-[200px]">
        <div className="font-medium mb-1">モーダル状態</div>
        {activeModals.length > 0 ? (
          <div className="space-y-1">
            {activeModals.map((modal) => (
              <div key={modal} className="text-green-400">
                ● {modal}モーダル
              </div>
            ))}
          </div>
        ) : (
          <div className="text-gray-400">すべて非表示</div>
        )}
        <div className="mt-2 text-[10px] text-gray-300">
          ESCで全て閉じる
        </div>
      </div>
    </div>
  );
}

// ========================================
// プレビュー・デバッグ用コンポーネント
// ========================================

/**
 * モーダル管理のデバッグ情報（開発用）
 */
export function TodayModalsPreview() {
  const modals = useTodayModals();

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <details className="p-4 border rounded-lg">
      <summary className="cursor-pointer font-medium">
        Today Modals Debug Info
      </summary>
      <div className="mt-2 space-y-3 text-xs">
        <div>
          <strong>Add Modal:</strong>
          <pre className="mt-1 p-2 bg-gray-100 rounded">
            {JSON.stringify(modals.addModal, null, 2)}
          </pre>
        </div>

        <div>
          <strong>Edit Modal:</strong>
          <pre className="mt-1 p-2 bg-gray-100 rounded">
            {JSON.stringify({
              isOpen: modals.editModal.isOpen,
              hasEditingItem: !!modals.editModal.editingMealItem,
              editingItemId: modals.editModal.editingMealItem?.id,
            }, null, 2)}
          </pre>
        </div>

        <div>
          <strong>Nutrition Modal:</strong>
          <pre className="mt-1 p-2 bg-gray-100 rounded">
            {JSON.stringify({
              isOpen: modals.nutritionModal.isOpen,
              hasData: !!modals.nutritionModal.data,
            }, null, 2)}
          </pre>
        </div>

        <div>
          <strong>Recommendation Modal:</strong>
          <pre className="mt-1 p-2 bg-gray-100 rounded">
            {JSON.stringify({
              isOpen: modals.recommendationModal.isOpen,
              hasRecommendation: !!modals.recommendationModal.recommendation,
            }, null, 2)}
          </pre>
        </div>

        <div>
          <strong>Utility States:</strong>
          <pre className="mt-1 p-2 bg-gray-100 rounded">
            {JSON.stringify({
              hasOpenModal: modals.hasOpenModal(),
              activeModalsCount: [
                modals.addModal.isOpen,
                modals.editModal.isOpen,
                modals.nutritionModal.isOpen,
                modals.recommendationModal.isOpen,
              ].filter(Boolean).length,
            }, null, 2)}
          </pre>
        </div>

        <div className="pt-2 space-x-2">
          <button
            onClick={() => modals.openAddModal('main', 1)}
            className="px-2 py-1 bg-blue-500 text-white rounded text-xs"
          >
            追加モーダル開く
          </button>
          <button
            onClick={() => modals.closeAllModals()}
            className="px-2 py-1 bg-red-500 text-white rounded text-xs"
          >
            全て閉じる
          </button>
        </div>
      </div>
    </details>
  );
}

// ========================================
// Placeholder Modal Component
// ========================================

interface PlaceholderModalProps {
  title: string;
  onClose: () => void;
  isOpen: boolean;
}

function PlaceholderModal({ title, onClose, isOpen }: PlaceholderModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        <div className="text-center py-8">
          <p className="text-gray-600 mb-4">
            このモーダルは将来実装予定です。
          </p>
          <p className="text-sm text-gray-500">
            現在はプレースホルダーとして表示されています。
          </p>
        </div>
        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            閉じる
          </button>
        </div>
      </div>
    </div>
  );
}