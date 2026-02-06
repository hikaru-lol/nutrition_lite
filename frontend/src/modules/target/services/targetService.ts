/**
 * targetService - Target関連のビジネスロジックとAPI処理
 *
 * 責務:
 * - Target取得のAPI呼び出し
 * - Target関連のビジネスロジック
 * - データ変換・バリデーション
 */

import { fetchActiveTarget, listTargets, deleteTarget, activateTarget } from '../api/targetClient';
import type { Target } from '../contract/targetContract';

// ========================================
// Service Interface
// ========================================

export interface ITargetService {
  /**
   * アクティブなターゲットを取得
   */
  getActiveTarget(): Promise<Target | null>;

  /**
   * ターゲット一覧を取得
   */
  getTargetsList(): Promise<Target[]>;

  /**
   * ターゲットを削除
   */
  deleteTarget(targetId: string): Promise<void>;

  /**
   * ターゲットをアクティブ化
   */
  activateTarget(targetId: string): Promise<void>;

  /**
   * ターゲットが栄養進捗表示に有効かチェック
   */
  validateTargetForProgress(target: Target | null): boolean;
}

// ========================================
// Service Implementation
// ========================================

export class TargetService implements ITargetService {
  async getActiveTarget(): Promise<Target | null> {
    try {
      const target = await fetchActiveTarget();
      return target || null;
    } catch (error) {
      console.error('Failed to fetch active target:', error);
      return null;
    }
  }

  async getTargetsList(): Promise<Target[]> {
    try {
      const response = await listTargets();
      return response.items;
    } catch (error) {
      console.error('Failed to fetch targets list:', error);
      return [];
    }
  }

  async deleteTarget(targetId: string): Promise<void> {
    if (!targetId || typeof targetId !== 'string') {
      throw new Error('Invalid target ID provided');
    }

    return deleteTarget(targetId);
  }

  async activateTarget(targetId: string): Promise<void> {
    if (!targetId || typeof targetId !== 'string') {
      throw new Error('Invalid target ID provided');
    }

    await activateTarget(targetId);
  }

  validateTargetForProgress(target: Target | null): boolean {
    if (!target) {
      return false;
    }

    // ターゲットに栄養素情報があるかチェック
    if (!target.nutrients || target.nutrients.length === 0) {
      return false;
    }

    // 必要な栄養素（PFC）が含まれているかチェック
    const requiredNutrients = ['protein', 'fat', 'carbohydrate'] as const;
    const targetNutrientCodes = target.nutrients.map(n => n.code);

    return requiredNutrients.some(required =>
      targetNutrientCodes.includes(required as any)
    );
  }
}

// ========================================
// Service Factory
// ========================================

/**
 * TargetServiceのシングルトンインスタンス作成
 */
let targetServiceInstance: TargetService | null = null;

export function getTargetService(): TargetService {
  if (!targetServiceInstance) {
    targetServiceInstance = new TargetService();
  }
  return targetServiceInstance;
}

// ========================================
// Hook for Service
// ========================================

/**
 * React Hook形式でTargetServiceを取得
 */
export function useTargetService(): TargetService {
  return getTargetService();
}

// ========================================
// Exports
// ========================================

export default TargetService;