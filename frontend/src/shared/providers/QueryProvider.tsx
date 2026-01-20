// src/shared/providers/QueryProvider.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode, useState } from 'react';
import { ApiError } from '../lib/api/fetcher';

export function QueryProvider({ children }: { children: ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // 401/403/404 はリトライしても直りにくいので止めるのが安全
            retry: (failureCount, err) => {
              if (err instanceof ApiError) {
                if ([401, 403, 404].includes(err.status)) return false;
              }
              return failureCount < 1; // 0〜1回程度
            },
            staleTime: 30_000,
            gcTime: 5 * 60_000,
            refetchOnWindowFocus: false,
          },
          mutations: {
            retry: false,
          },
        },
      })
  );

  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
