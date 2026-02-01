import { clientApiFetch } from '@/shared/api/client';
import {
  TargetSchema,
  TargetListResponseSchema,
  CreateTargetRequestSchema,
  type Target,
  type TargetListResponse,
  type CreateTargetRequest,
} from '../contract/targetContract';

export async function fetchActiveTarget(): Promise<Target | null> {
  try {
    const raw = await clientApiFetch<unknown>(`/targets/active`, {
      method: 'GET',
    });
    return TargetSchema.parse(raw);
  } catch (err) {
    // 404 = active target が無い（初回等） → null で扱うのが Today 的に便利
    if (err instanceof Error && err.message.includes('404')) {
      return null;
    }
    throw err;
  }
}

export async function listTargets(params?: {
  limit?: number;
  offset?: number;
}): Promise<TargetListResponse> {
  const qs = new URLSearchParams();
  if (params?.limit != null) qs.set('limit', String(params.limit));
  if (params?.offset != null) qs.set('offset', String(params.offset));

  const raw = await clientApiFetch<unknown>(
    `/targets${qs.toString() ? `?${qs.toString()}` : ''}`,
    { method: 'GET' }
  );
  return TargetListResponseSchema.parse(raw);
}

export async function createTarget(req: CreateTargetRequest): Promise<Target> {
  const safe = CreateTargetRequestSchema.parse(req);
  const raw = await clientApiFetch<unknown>(`/targets`, {
    method: 'POST',
    body: safe,
  });
  return TargetSchema.parse(raw);
}

export async function activateTarget(targetId: string): Promise<Target> {
  const raw = await clientApiFetch<unknown>(`/targets/${targetId}/activate`, {
    method: 'POST',
  });
  return TargetSchema.parse(raw);
}

export async function deleteTarget(targetId: string): Promise<void> {
  await clientApiFetch<unknown>(`/targets/${targetId}`, {
    method: 'DELETE',
  });
}
