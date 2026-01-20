// src/shared/lib/query/invalidate.ts
import type { QueryClient } from '@tanstack/react-query';
import { qk } from './keys';

export async function invalidateAfterTargetSaved(qc: QueryClient) {
  await qc.invalidateQueries({ queryKey: qk.target.current() });
  // today summary / reports も後でここに足す
}
