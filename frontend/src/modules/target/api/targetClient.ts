import { clientApiFetch } from '@/shared/api/client';
import {
  TargetResponseSchema,
  TargetListResponseSchema,
  type CreateTargetRequest,
  type TargetResponse,
  type TargetListResponse,
} from '../contract/targetContract';

/**
 * POST /targets - 新しい Target を作成
 */
export async function createTarget(
  body: CreateTargetRequest
): Promise<TargetResponse> {
  const raw = await clientApiFetch<unknown>('/targets', {
    method: 'POST',
    body,
  });
  return TargetResponseSchema.parse(raw);
}

/**
 * GET /targets - Target 一覧を取得
 */
export async function fetchTargets(): Promise<TargetListResponse> {
  const raw = await clientApiFetch<unknown>('/targets', { method: 'GET' });
  return TargetListResponseSchema.parse(raw);
}

/**
 * GET /targets/active - アクティブな Target を取得
 * 404 の場合は null を返す
 */
export async function fetchActiveTarget(): Promise<TargetResponse | null> {
  try {
    const raw = await clientApiFetch<unknown>('/targets/active', {
      method: 'GET',
    });
    return TargetResponseSchema.parse(raw);
  } catch (err) {
    if (err instanceof Error && err.message.includes('TARGET_NOT_FOUND')) {
      return null;
    }
    throw err;
  }
}

/**
 * POST /targets/:id/activate - 指定した Target をアクティブにする
 */
export async function activateTarget(
  targetId: string
): Promise<TargetResponse> {
  const raw = await clientApiFetch<unknown>(`/targets/${targetId}/activate`, {
    method: 'POST',
  });
  return TargetResponseSchema.parse(raw);
}
