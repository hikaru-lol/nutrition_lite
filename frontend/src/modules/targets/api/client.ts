// src/modules/target/api/client.ts
import { apiFetch } from '@/shared/lib/api/fetcher';
import type {
  CreateTargetRequest,
  TargetListResponse,
  TargetResponse,
  UpdateTargetRequest,
} from './types';

export const targetApi = {
  list: (params?: { limit?: number; offset?: number }) => {
    const qs = new URLSearchParams();
    if (params?.limit != null) qs.set('limit', String(params.limit));
    if (params?.offset != null) qs.set('offset', String(params.offset));
    const suffix = qs.toString() ? `?${qs.toString()}` : '';
    return apiFetch<TargetListResponse>(`/targets${suffix}`);
  },

  create: (body: CreateTargetRequest) =>
    apiFetch<TargetResponse>('/targets', { method: 'POST', body }),

  getActive: () => apiFetch<TargetResponse>('/targets/active'),

  getById: (targetId: string) =>
    apiFetch<TargetResponse>(`/targets/${targetId}`),

  update: (targetId: string, body: UpdateTargetRequest) =>
    apiFetch<TargetResponse>(`/targets/${targetId}`, { method: 'PATCH', body }),

  activate: (targetId: string) =>
    apiFetch<TargetResponse>(`/targets/${targetId}/activate`, {
      method: 'POST',
    }),
};
