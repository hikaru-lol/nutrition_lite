// src/modules/target/model/keys.ts
export const targetKeys = {
  all: ['target'] as const,
  list: (p?: { limit?: number; offset?: number }) =>
    [...targetKeys.all, 'list', p ?? {}] as const,
  active: () => [...targetKeys.all, 'active'] as const,
  byId: (id: string) => [...targetKeys.all, 'byId', id] as const,
};
