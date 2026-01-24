import { clientApiFetch } from '@/shared/api/client';
import type { GenerateTargetRequest } from '../contract/targetContract';

export type TargetResult = {
  calories: number;
  proteinG: number;
  fatG: number;
  carbsG: number;
};

export async function generateTarget(req: GenerateTargetRequest) {
  return clientApiFetch<TargetResult>('/target/generate', {
    method: 'POST',
    body: req,
  });
}
