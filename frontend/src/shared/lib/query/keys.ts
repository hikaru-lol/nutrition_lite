// src/shared/lib/query/keys.ts
export const qk = {
  auth: {
    me: () => ['auth', 'me'] as const,
  },
  target: {
    current: () => ['target', 'current'] as const,
  },
  mealRecommendation: {
    list: (limit?: number) => ['meal-recommendation', 'list', limit] as const,
    byDate: (date: string) => ['meal-recommendation', 'by-date', date] as const,
    latest: () => ['meal-recommendation', 'latest'] as const,
  },
  // meals / reports は後で追加
};
