// src/app/providers.tsx
'use client';

import React from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { createQueryClient } from '@/shared/lib/query/queryClient';

export function Providers(props: { children: React.ReactNode }) {
  const [qc] = React.useState(() => createQueryClient());

  return (
    <QueryClientProvider client={qc}>
      {props.children}
      <Toaster richColors position="top-right" />
    </QueryClientProvider>
  );
}
