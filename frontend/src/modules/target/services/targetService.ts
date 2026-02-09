/**
 * targetService - Target関連のビジネスロジックとAPI処理
 */

import { fetchActiveTarget, listTargets, createTarget, deleteTarget, activateTarget } from '../api/targetClient';
import type { Target, CreateTargetRequest } from '../contract/targetContract';

export interface ITargetService {
  getActiveTarget(): Promise<Target | null>;
  getTargetsList(): Promise<Target[]>;
  createTarget(data: CreateTargetRequest): Promise<Target>;
  deleteTarget(targetId: string): Promise<void>;
  activateTarget(targetId: string): Promise<void>;
  validateTargetForProgress(target: Target | null): boolean;
}

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

  async createTarget(data: CreateTargetRequest): Promise<Target> {
    return createTarget(data);
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
    if (!target?.nutrients?.length) return false;

    const requiredNutrients = ['protein', 'fat', 'carbohydrate'] as const;
    const targetNutrientCodes = target.nutrients.map(n => n.code);

    return requiredNutrients.some(required => targetNutrientCodes.includes(required as any));
  }
}

export function useTargetService(): TargetService {
  return new TargetService();
}

export default TargetService;
