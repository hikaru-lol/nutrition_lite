// src/modules/auth/api/types.ts
export type UserPlan = 'trial' | 'free' | 'paid';

export type UserSummary = {
  id: string;
  email: string;
  name: string | null;
  plan: UserPlan;
  trial_ends_at: string | null;
  has_profile: boolean;
  created_at: string;
};

export type AuthUserResponse = {
  user: UserSummary;
};

export type RegisterRequest = {
  email: string;
  password: string;
  name?: string | null;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type RefreshResponse = {
  ok: boolean;
  user: UserSummary;
};
