// src/app/providers.tsx
'use client';

import React from 'react';
import '@/modules/auth/api/authClient'; // ✅ refresh 登録の副作用を起動
import { QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { createQueryClient } from '@/shared/lib/query/queryClient';
import { ThemeProvider } from '@/shared/providers/ThemeProvider';

export function Providers(props: { children: React.ReactNode }) {
  const [qc] = React.useState(() => createQueryClient());

  return (
    <ThemeProvider>
      <QueryClientProvider client={qc}>
        {props.children}
        <Toaster richColors position="top-right" />
      </QueryClientProvider>
    </ThemeProvider>
  );
}
