// src/shared/lib/query/invalidate.ts
import type { QueryClient } from '@tanstack/react-query';
import { qk } from '@/shared/lib/query/keys';

export async function invalidateAfterTargetSaved(qc: QueryClient) {
  await qc.invalidateQueries({ queryKey: qk.target.current() });
  await qc.invalidateQueries({ queryKey: qk.auth.me() }); // ✅ has_target 等の反映
}
