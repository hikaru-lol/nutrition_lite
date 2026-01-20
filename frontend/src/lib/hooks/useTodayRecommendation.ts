// frontend/lib/hooks/useTodayRecommendation.ts
'use client';

import { useEffect, useState } from 'react';
import {
  fetchLatestRecommendation,
  type RecommendationResponseApi,
} from '@/lib/api/recommendation';
import { fetchMe, type CurrentUser } from '@/lib/api/auth';
import { ApiError } from '@/lib/api/client';
import type { UserPlan } from '@/lib/api/auth';

export type Plan = UserPlan;

export type TodayRecommendationVM = {
  date: string; // 提案対象日
  body: string;
  tips: string[];
};

export type TodayRecommendationState = {
  plan: Plan;
  hasRecommendation: boolean;
  recommendation?: TodayRecommendationVM;
};

export function useTodayRecommendation() {
  const [data, setData] = useState<TodayRecommendationState | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // プランを確認
        const user = await fetchMe();
        if (cancelled) return;

        const base: TodayRecommendationState = {
          plan: user.plan,
          hasRecommendation: false,
        };

        // FREE プランなら「ロック状態」として返す
        if (user.plan === 'free') {
          setData(base);
          return;
        }

        // TRIAL / PAID → 最新の提案を取得
        let reco: RecommendationResponseApi | null = null;
        try {
          reco = await fetchLatestRecommendation();
        } catch (e) {
          if (e instanceof ApiError && e.status === 404) {
            // まだ提案がない
            setData(base);
            return;
          }
          throw e;
        }

        if (cancelled) return;

        if (!reco) {
          setData(base);
          return;
        }

        const vm: TodayRecommendationState = {
          plan: user.plan,
          hasRecommendation: true,
          recommendation: {
            date: reco.generated_for_date,
            body: reco.body,
            tips: reco.tips,
          },
        };

        setData(vm);
      } catch (e: any) {
        if (cancelled) return;
        console.error("Failed to fetch today's recommendation", e);
        setError(
          e instanceof Error ? e : new Error('Failed to load recommendation')
        );
        setData(null);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return { data, isLoading, error };
}
