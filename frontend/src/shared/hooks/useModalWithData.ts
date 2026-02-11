/**
 * useModalWithData - データ付きモーダル用フック
 *
 * 責務:
 * - モーダルの開閉状態管理
 * - モーダルに渡すデータの管理
 * - 型安全なデータアクセス
 */

'use client';

import { useState, useCallback } from 'react';

// ========================================
// Types
// ========================================

export interface ModalWithDataState<T = any> {
  /** モーダルが開いているかどうか */
  isOpen: boolean;
  /** モーダルに渡されているデータ */
  data: T | null;
  /** モーダルを開く（データ付き） */
  open: (data: T) => void;
  /** モーダルを閉じる（データもクリア） */
  close: () => void;
}

// ========================================
// Hook Options
// ========================================

export interface UseModalWithDataOptions<T> {
  /** 初期データ */
  initialData?: T | null;
  /** モーダルを閉じるときのコールバック */
  onClose?: () => void;
  /** モーダルを開くときのコールバック */
  onOpen?: (data: T) => void;
}

// ========================================
// Main Hook
// ========================================

/**
 * データ付きモーダルの状態を管理するフック
 *
 * @param options - フックのオプション
 * @returns モーダル状態とアクション
 *
 * @example
 * ```tsx
 * interface MyData { id: string; name: string; }
 *
 * const modal = useModalWithData<MyData>();
 *
 * // モーダルを開く
 * const handleOpen = (item: MyData) => {
 *   modal.open(item);
 * };
 *
 * // レンダリング
 * {modal.isOpen && modal.data && (
 *   <MyModal
 *     isOpen={modal.isOpen}
 *     data={modal.data}
 *     onClose={modal.close}
 *   />
 * )}
 * ```
 */
export function useModalWithData<T = any>(
  options: UseModalWithDataOptions<T> = {}
): ModalWithDataState<T> {
  const { initialData = null, onClose, onOpen } = options;

  // ========================================
  // State
  // ========================================

  const [isOpen, setIsOpen] = useState(false);
  const [data, setData] = useState<T | null>(initialData);

  // ========================================
  // Actions
  // ========================================

  const open = useCallback((newData: T) => {
    setData(newData);
    setIsOpen(true);
    onOpen?.(newData);
  }, [onOpen]);

  const close = useCallback(() => {
    setIsOpen(false);
    setData(null);
    onClose?.();
  }, [onClose]);

  // ========================================
  // Return
  // ========================================

  return {
    isOpen,
    data,
    open,
    close,
  };
}

// ========================================
// ユーティリティ関数
// ========================================

/**
 * モーダル状態のデバッグ情報を取得
 */
export function getModalDebugInfo<T>(
  modal: ModalWithDataState<T>,
  name: string = 'Modal'
): Record<string, any> {
  return {
    name,
    isOpen: modal.isOpen,
    hasData: modal.data !== null,
    dataKeys: modal.data && typeof modal.data === 'object'
      ? Object.keys(modal.data)
      : null,
  };
}

/**
 * 複数モーダルの競合チェック
 */
export function hasModalConflict(...modals: ModalWithDataState<any>[]): boolean {
  const openCount = modals.filter(modal => modal.isOpen).length;
  return openCount > 1;
}