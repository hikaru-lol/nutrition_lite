// src/modules/meal/model/keys.ts
export const mealKeys = {
  all: ['meal'] as const,
  itemsByDate: (date: string) =>
    [...mealKeys.all, 'itemsByDate', date] as const,
};
