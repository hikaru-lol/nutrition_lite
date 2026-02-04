'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import {
  getCurrentPlanInfo,
  redirectToCheckout,
  redirectToBillingPortal,
} from '../api/billingClient';
import type { CurrentPlanInfo } from '../contract/billingContract';
import { ApiError } from '@/shared/lib/errors';

// ========================================
// Query Keys
// ========================================

const billingKeys = {
  all: () => ['billing'] as const,
  currentPlan: () => [...billingKeys.all(), 'current-plan'] as const,
} as const;

// ========================================
// プラン情報取得Hook
// ========================================

export function useBillingPageModel() {
  const queryClient = useQueryClient();
  const router = useRouter();

  // 現在のプラン情報取得
  const planQuery = useQuery<CurrentPlanInfo>({
    queryKey: billingKeys.currentPlan(),
    queryFn: getCurrentPlanInfo,
    staleTime: 1000 * 60 * 5, // 5分間キャッシュ
    retry: (failureCount, error) => {
      if (error instanceof ApiError && error.status === 401) {
        return false; // 認証エラーは再試行しない
      }
      return failureCount < 3;
    },
  });


  // Checkout リダイレクト
  const checkoutMutation = useMutation({
    mutationFn: ({ idempotencyKey }: { idempotencyKey?: string } = {}) =>
      redirectToCheckout(idempotencyKey),
    onMutate: () => {
      toast.loading('決済画面に移動しています...', {
        id: 'checkout-loading',
      });
    },
    onError: (error) => {
      toast.dismiss('checkout-loading');

      if (error instanceof ApiError) {
        switch (error.status) {
          case 401:
            toast.error('ログインが必要です');
            router.push('/auth/login');
            break;
          case 400:
            toast.error('課金アカウントの設定に問題があります');
            break;
          case 500:
            toast.error('決済画面の作成に失敗しました');
            break;
          default:
            toast.error('決済処理でエラーが発生しました');
        }
      } else {
        toast.error('ネットワークエラーが発生しました');
      }
    },
    onSuccess: () => {
      toast.dismiss('checkout-loading');
      // リダイレクトが実行されるのでここでは何もしない
    },
  });

  // Billing Portal リダイレクト
  const portalMutation = useMutation({
    mutationFn: redirectToBillingPortal,
    onMutate: () => {
      toast.loading('管理画面に移動しています...', {
        id: 'portal-loading',
      });
    },
    onError: (error) => {
      toast.dismiss('portal-loading');

      if (error instanceof ApiError) {
        switch (error.status) {
          case 401:
            toast.error('ログインが必要です');
            router.push('/auth/login');
            break;
          case 400:
            toast.error('課金管理画面にアクセスできません。まずプレミアムプランにご登録ください。');
            break;
          default:
            toast.error('管理画面の表示に失敗しました');
        }
      } else {
        toast.error('ネットワークエラーが発生しました');
      }
    },
    onSuccess: () => {
      toast.dismiss('portal-loading');
      // リダイレクトが実行されるのでここでは何もしない
    },
  });

  // プラン情報の再取得
  const refreshPlanInfo = () => {
    return queryClient.invalidateQueries({
      queryKey: billingKeys.currentPlan(),
    });
  };

  // 決済完了後の処理（Success pageで使用）
  const handlePaymentSuccess = () => {
    toast.success('プレミアムプランへのアップグレードが完了しました！');
    refreshPlanInfo();
    router.push('/today'); // ダッシュボードにリダイレクト
  };

  // 決済キャンセル後の処理（Cancel pageで使用）
  const handlePaymentCancel = () => {
    toast.info('決済をキャンセルしました');
    router.push('/billing/plan'); // プラン選択画面に戻る
  };

  return {
    // データ
    planInfo: planQuery.data,
    isPlanLoading: planQuery.isLoading,
    isPlanError: planQuery.isError,
    planError: planQuery.error,

    // 状態
    isCheckoutPending: checkoutMutation.isPending,
    isPortalPending: portalMutation.isPending,

    // アクション
    startCheckout: checkoutMutation.mutate,
    openBillingPortal: portalMutation.mutate,
    refreshPlanInfo,
    handlePaymentSuccess,
    handlePaymentCancel,

    // ヘルパー
    isPremium: planQuery.data ?
      (planQuery.data.user_plan === 'paid' || planQuery.data.is_trial_active) : false,
    isFree: planQuery.data ?
      (planQuery.data.user_plan === 'free' && !planQuery.data.is_trial_active) : false,
    displayPlanName: planQuery.data ? (() => {
      if (planQuery.data.is_trial_active) return 'トライアル';
      switch (planQuery.data.user_plan) {
        case 'paid': return 'プレミアム';
        case 'trial': return 'トライアル';
        case 'free':
        default: return 'フリー';
      }
    })() : null,
  };
}

// ========================================
// 機能制限チェック専用Hook
// ========================================

export function useFeatureLimitCheck() {
  const { planInfo } = useBillingPageModel();

  const checkMealRecommendationLimit = (currentCount: number) => {
    if (!planInfo) {
      return { allowed: false, limit: 0, remaining: 0, requiresUpgrade: true };
    }

    // プレミアムまたはトライアル中は無制限
    if (planInfo.user_plan === 'paid' || planInfo.is_trial_active) {
      return { allowed: true, limit: null, remaining: null, requiresUpgrade: false };
    }

    // フリープランは月5回まで
    const limit = 5;
    const remaining = Math.max(0, limit - currentCount);
    const allowed = currentCount < limit;

    return {
      allowed,
      limit,
      remaining,
      requiresUpgrade: !allowed
    };
  };

  const checkDetailedAnalysisAccess = () => {
    if (!planInfo) {
      return { allowed: false, requiresUpgrade: true };
    }

    const allowed = planInfo.user_plan === 'paid' || planInfo.is_trial_active;
    return { allowed, requiresUpgrade: !allowed };
  };

  return {
    checkMealRecommendationLimit,
    checkDetailedAnalysisAccess,
  };
}

// ========================================
// 軽量版Hook（プラン情報のみ）
// ========================================

export function useCurrentPlan() {
  return useQuery<CurrentPlanInfo>({
    queryKey: billingKeys.currentPlan(),
    queryFn: getCurrentPlanInfo,
    staleTime: 1000 * 60 * 5, // 5分間キャッシュ
  });
}