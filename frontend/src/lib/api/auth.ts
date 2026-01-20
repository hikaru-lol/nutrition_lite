// frontend/lib/api/auth.ts
import { apiGet, apiPost } from './client';

export type UserPlan = 'trial' | 'free' | 'paid';

export type UserSummaryApi = {
  id: string;
  email: string;
  name: string | null;
  plan: UserPlan;
  trial_ends_at: string | null;
  has_profile: boolean;
  created_at: string;
};

export type AuthUserResponse = {
  user: UserSummaryApi;
};

export type RefreshResponse = {
  ok: boolean;
  user: UserSummaryApi;
};

export type CurrentUser = {
  id: string;
  email: string;
  name: string | null;
  plan: UserPlan;
  trialEndsAt: string | null;
  hasProfile: boolean;
  createdAt: string;
};

function toCurrentUser(api: UserSummaryApi): CurrentUser {
  return {
    id: api.id,
    email: api.email,
    name: api.name,
    plan: api.plan,
    trialEndsAt: api.trial_ends_at,
    hasProfile: api.has_profile,
    createdAt: api.created_at,
  };
}

export async function login(
  email: string,
  password: string
): Promise<CurrentUser> {
  const res = await apiPost<AuthUserResponse>('/auth/login', {
    email,
    password,
  });
  return toCurrentUser(res.user);
}

export async function register(
  name: string | null,
  email: string,
  password: string
): Promise<CurrentUser> {
  const res = await apiPost<AuthUserResponse>('/auth/register', {
    email,
    password,
    name,
  });
  return toCurrentUser(res.user);
}

export async function fetchMe(): Promise<CurrentUser> {
  const res = await apiGet<AuthUserResponse>('/auth/me');
  return toCurrentUser(res.user);
}

export async function logout(): Promise<void> {
  await apiPost<void>('/auth/logout');
}
