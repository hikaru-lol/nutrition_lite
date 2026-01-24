// src/shared/lib/query/keys.ts
export const qk = {
  auth: {
    me: () => ['auth', 'me'] as const,
  },
  target: {
    current: () => ['target', 'current'] as const,
  },
  // meals / reports は後で追加
};
