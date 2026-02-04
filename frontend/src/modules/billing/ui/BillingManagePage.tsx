'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Crown,
  Settings,
  Calendar,
  ExternalLink,
  AlertCircle,
  Info,
  Shield,
  CreditCard,
  User
} from 'lucide-react';
import { useBillingPageModel } from '../model/useBillingPageModel';
import { PLAN_DEFINITIONS } from '../contract/billingContract';

// ========================================
// メインコンポーネント
// ========================================

export function BillingManagePage() {
  const {
    planInfo,
    isPlanLoading,
    isPlanError,
    isPortalPending,
    openBillingPortal,
    isPremium,
    isFree,
    displayPlanName
  } = useBillingPageModel();

  // ローディング状態
  if (isPlanLoading) {
    return <BillingManagePageSkeleton />;
  }

  // エラー状態
  if (isPlanError) {
    return (
      <div className="mx-auto w-full max-w-4xl p-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>エラー</AlertTitle>
          <AlertDescription>
            課金情報の取得に失敗しました。ページを再読み込みしてください。
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!planInfo) return null;

  return (
    <div className="mx-auto w-full max-w-4xl p-6 space-y-8">
      {/* ページヘッダー */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">課金管理</h1>
        <p className="text-muted-foreground">
          プランの確認や課金設定の管理を行えます
        </p>
      </div>

      {/* 現在のプラン情報 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            現在のプラン
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <Badge
                  variant={isPremium ? "default" : "secondary"}
                  className="gap-2 text-base py-1 px-3"
                >
                  {isPremium && <Crown className="h-4 w-4" />}
                  {displayPlanName}
                </Badge>

                {planInfo.is_trial_active && planInfo.trial_ends_at && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Calendar className="h-4 w-4" />
                    <span>
                      トライアル終了: {new Date(planInfo.trial_ends_at).toLocaleDateString('ja-JP')}
                    </span>
                  </div>
                )}
              </div>

              <div className="text-sm text-muted-foreground">
                {isPremium
                  ? PLAN_DEFINITIONS.paid.description
                  : PLAN_DEFINITIONS.free.description
                }
              </div>

              {isPremium && (
                <div className="text-sm text-green-600">
                  プレミアム機能をすべてご利用いただけます
                </div>
              )}
            </div>

            <div className="text-right">
              <div className="text-2xl font-bold">
                {isPremium ? PLAN_DEFINITIONS.paid.price : PLAN_DEFINITIONS.free.price}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 利用可能機能 */}
      <Card>
        <CardHeader>
          <CardTitle>ご利用可能な機能</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3">
            {(isPremium ? PLAN_DEFINITIONS.paid.features : PLAN_DEFINITIONS.free.features).map((feature, index) => (
              <div key={index} className="flex items-center gap-3">
                <div className="w-2 h-2 bg-primary rounded-full flex-shrink-0" />
                <span className="text-sm">{feature}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 課金管理セクション */}
      {isPremium ? (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              サブスクリプション管理
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              支払い方法の変更、請求履歴の確認、プランの解約などは
              Stripe Billing Portalで行えます。
            </p>

            <Button
              onClick={() => openBillingPortal()}
              disabled={isPortalPending}
              className="gap-2"
            >
              <CreditCard className="h-4 w-4" />
              {isPortalPending ? '処理中...' : '課金管理画面を開く'}
              <ExternalLink className="h-4 w-4" />
            </Button>

            <div className="text-xs text-muted-foreground space-y-1">
              <p>• 支払い方法の追加・変更</p>
              <p>• 請求履歴とレシートのダウンロード</p>
              <p>• プランの変更・解約</p>
              <p>• 次回請求日の確認</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Crown className="h-5 w-5" />
              プレミアムプランにアップグレード
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              プレミアムプランで、すべての機能をお楽しみください。
            </p>

            <div className="grid gap-2 text-sm">
              {PLAN_DEFINITIONS.paid.features.slice(1).map((feature, index) => (
                <div key={index} className="flex items-center gap-3 text-muted-foreground">
                  <Crown className="h-4 w-4 text-yellow-500 flex-shrink-0" />
                  <span>{feature}</span>
                </div>
              ))}
            </div>

            <Button
              className="w-full gap-2"
              onClick={() => window.location.href = '/billing/plan'}
            >
              <Crown className="h-4 w-4" />
              プレミアムプランを見る
            </Button>
          </CardContent>
        </Card>
      )}

      {/* β版情報 */}
      <Alert className="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950">
        <Info className="h-4 w-4" />
        <AlertTitle>β版テスト中</AlertTitle>
        <AlertDescription className="space-y-2">
          <p>
            現在β版として運用中のため、実際の課金処理は発生していません。
            すべての機能をお試しいただけます。
          </p>
          {isPremium && (
            <p>
              正式版リリース時には、設定を引き継いでご利用いただけます。
            </p>
          )}
        </AlertDescription>
      </Alert>

      {/* セキュリティ情報 */}
      <Card className="border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <Shield className="h-5 w-5 text-green-600 mt-0.5" />
            <div className="space-y-2">
              <h3 className="font-medium text-green-800 dark:text-green-200">
                安全な決済システム
              </h3>
              <p className="text-sm text-green-700 dark:text-green-300">
                すべての決済処理は、業界標準のセキュリティを誇るStripe社のシステムを使用しています。
                クレジットカード情報は当サービスには保存されません。
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ========================================
// ローディング用スケルトン
// ========================================

function BillingManagePageSkeleton() {
  return (
    <div className="mx-auto w-full max-w-4xl p-6 space-y-8">
      {/* ヘッダースケルトン */}
      <div className="text-center space-y-2">
        <Skeleton className="h-10 w-32 mx-auto" />
        <Skeleton className="h-6 w-64 mx-auto" />
      </div>

      {/* プラン情報スケルトン */}
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between">
            <div className="space-y-2">
              <Skeleton className="h-8 w-24" />
              <Skeleton className="h-4 w-48" />
              <Skeleton className="h-4 w-32" />
            </div>
            <Skeleton className="h-8 w-16" />
          </div>
        </CardContent>
      </Card>

      {/* 機能リストスケルトン */}
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-40" />
        </CardHeader>
        <CardContent className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex items-center gap-3">
              <Skeleton className="h-2 w-2 rounded-full" />
              <Skeleton className="h-4 flex-1" />
            </div>
          ))}
        </CardContent>
      </Card>

      {/* 管理セクションスケルトン */}
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-10 w-40" />
          <div className="space-y-1">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-3 w-32" />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}