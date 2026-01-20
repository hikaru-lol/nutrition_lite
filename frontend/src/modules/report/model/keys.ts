// src/modules/report/model/keys.ts
export const reportKeys = {
  all: ['report'] as const,
  byDate: (date: string) => [...reportKeys.all, 'byDate', date] as const,
};
