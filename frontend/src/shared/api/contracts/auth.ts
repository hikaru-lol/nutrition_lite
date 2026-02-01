// src/shared/api/contracts/auth.ts
export type UserPlan = 'trial' | 'free' | 'paid';

export type UserSummary = {
  id: string;
  email: string;
  name: string | null;
  plan: UserPlan;

  // Phase3のガード判定に使う（バックエンドに無ければ後で差し替え）
  has_profile: boolean;
  has_target: boolean;

  created_at: string;
};

export type CurrentUserResponse = {
  user: UserSummary;
};

export type RefreshResponse = {
  ok: boolean;
  user: UserSummary;
};
