// src/modules/target/api/targetApi.ts
import { apiFetch } from '@/shared/api/client';
import type {
  TargetGenerateRequest,
  TargetGenerateResponse,
  TargetSaveRequest,
  TargetSaveResponse,
} from '@/shared/api/contracts';

export async function generateTarget(req: TargetGenerateRequest) {
  return apiFetch<TargetGenerateResponse>('/api/v1/targets/generate', {
    method: 'POST',
    body: req,
  });
}

export async function saveTarget(req: TargetSaveRequest) {
  return apiFetch<TargetSaveResponse>('/api/v1/targets', {
    method: 'POST',
    body: req,
  });
}
