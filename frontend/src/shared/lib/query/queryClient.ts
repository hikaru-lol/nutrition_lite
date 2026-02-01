// src/shared/lib/query/queryClient.ts
'use client';

import { QueryClient } from '@tanstack/react-query';

export function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        retry: (failureCount, error: any) => {
          // unauthorized はリトライしない（refreshは apiFetch が担当）
          if (error?.kind === 'unauthorized' || error?.kind === 'forbidden')
            return false;
          return failureCount < 2;
        },
        refetchOnWindowFocus: false,
      },
      mutations: {
        retry: 0,
      },
    },
  });
}
