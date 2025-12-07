export type CurrentUser = {
  id: string;
  name: string;
  plan: 'trial' | 'free' | 'paid';
  trialEndsAt?: string | null;
  hasProfile: boolean;
};

export function useCurrentUser(): {
  user: CurrentUser | null;
  isLoading: boolean;
} {
  // 実装は後でAPI連携
  return { user: null, isLoading: true };
}
