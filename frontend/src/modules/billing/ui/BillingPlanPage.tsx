'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Check,
  Crown,
  Zap,
  AlertCircle,
  Info,
  CreditCard,
  Shield
} from 'lucide-react';
import { useBillingPageModel } from '../model/useBillingPageModel';
import { PLAN_DEFINITIONS, BETA_NOTICE } from '../contract/billingContract';

// ========================================
// メインコンポーネント
// ========================================

export function BillingPlanPage() {
  const {
    planInfo,
    isPlanLoading,
    isPlanError,
    planError,
    isCheckoutPending,
    startCheckout,
    isPremium,
    displayPlanName
  } = useBillingPageModel();


  // ローディング状態
  if (isPlanLoading) {
    return <BillingPlanPageSkeleton />;
  }

  // エラー状態
  if (isPlanError) {
    return (
      <div className="mx-auto w-full max-w-4xl p-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>エラー</AlertTitle>
          <AlertDescription>
            プラン情報の取得に失敗しました。ページを再読み込みしてください。
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-6xl p-6 space-y-8">
      {/* ページヘッダー */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold">料金プラン</h1>
        <p className="text-muted-foreground text-lg">
          あなたに最適なプランを選択してください
        </p>

        {/* 現在のプラン表示 */}
        {planInfo && (
          <div className="flex items-center justify-center gap-2">
            <span className="text-sm text-muted-foreground">現在のプラン:</span>
            <Badge variant={isPremium ? "default" : "secondary"} className="gap-1">
              {isPremium && <Crown className="h-3 w-3" />}
              {displayPlanName}
            </Badge>
          </div>
        )}
      </div>

      {/* β版お知らせ */}
      <Alert className="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950">
        <Info className="h-4 w-4" />
        <AlertTitle>{BETA_NOTICE.title}</AlertTitle>
        <AlertDescription className="space-y-2">
          <p>{BETA_NOTICE.message}</p>
          <div className="flex items-center gap-2 text-sm">
            <CreditCard className="h-4 w-4" />
            <span>テストカード番号:</span>
            <code className="bg-blue-100 dark:bg-blue-900 px-2 py-1 rounded text-xs">
              {BETA_NOTICE.testCard}
            </code>
          </div>
        </AlertDescription>
      </Alert>

      {/* プラン比較 */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* フリープラン */}
        <PlanCard
          plan="free"
          planData={PLAN_DEFINITIONS.free}
          currentPlan={planInfo?.user_plan}
          isPremiumActive={isPremium}
          onSelectPlan={null} // フリープランは選択不可
          isLoading={false}
        />

        {/* プレミアムプラン */}
        <PlanCard
          plan="paid"
          planData={PLAN_DEFINITIONS.paid}
          currentPlan={planInfo?.user_plan}
          isPremiumActive={isPremium}
          onSelectPlan={() => startCheckout()}
          isLoading={isCheckoutPending}
        />
      </div>

      {/* 注意事項 */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
          <Shield className="h-4 w-4" />
          <span>安全なStripe決済システムを使用</span>
        </div>
        <p className="text-xs text-muted-foreground max-w-2xl mx-auto">
          プレミアムプランはいつでもキャンセル可能です。
          課金管理画面から簡単に解約やプラン変更を行えます。
        </p>
      </div>
    </div>
  );
}

// ========================================
// プランカードコンポーネント
// ========================================

interface PlanCardProps {
  plan: 'free' | 'paid';
  planData: typeof PLAN_DEFINITIONS.free | typeof PLAN_DEFINITIONS.paid;
  currentPlan?: string;
  isPremiumActive?: boolean;
  onSelectPlan: (() => void) | null;
  isLoading: boolean;
}

function PlanCard({
  plan,
  planData,
  currentPlan,
  isPremiumActive,
  onSelectPlan,
  isLoading
}: PlanCardProps) {
  const isCurrentPlan =
    (plan === 'free' && currentPlan === 'free' && !isPremiumActive) ||
    (plan === 'paid' && isPremiumActive);

  const isPopular = 'isPopular' in planData && planData.isPopular;

  return (
    <Card className={`relative transition-all duration-200 ${
      isPopular
        ? 'border-primary shadow-lg scale-105'
        : 'border-border hover:border-primary/50'
    }`}>
      {/* Popular バッジ */}
      {isPopular && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2">
          <Badge className="gap-1 bg-primary">
            <Crown className="h-3 w-3" />
            おすすめ
          </Badge>
        </div>
      )}

      <CardHeader className="text-center pb-4">
        <CardTitle className="flex items-center justify-center gap-2">
          {plan === 'paid' && <Zap className="h-5 w-5 text-primary" />}
          {planData.name}
        </CardTitle>
        <div className="space-y-2">
          <div className="text-3xl font-bold">
            {planData.price}
          </div>
          <p className="text-muted-foreground text-sm">
            {planData.description}
          </p>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* 機能リスト */}
        <div className="space-y-3">
          {planData.features.map((feature, index) => (
            <div key={index} className="flex items-start gap-3">
              <Check className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
              <span className="text-sm">{feature}</span>
            </div>
          ))}
        </div>

        {/* 制限事項（フリープランのみ） */}
        {'limitations' in planData && planData.limitations && (
          <div className="space-y-3 pt-3 border-t">
            <p className="text-sm font-medium text-muted-foreground">制限事項:</p>
            {planData.limitations.map((limitation, index) => (
              <div key={index} className="flex items-start gap-3">
                <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-muted-foreground">{limitation}</span>
              </div>
            ))}
          </div>
        )}

        {/* アクションボタン */}
        <div className="pt-4">
          {isCurrentPlan ? (
            <Button disabled className="w-full">
              現在のプラン
            </Button>
          ) : onSelectPlan ? (
            <Button
              onClick={onSelectPlan}
              disabled={isLoading}
              className="w-full"
              size="lg"
            >
              {isLoading ? '処理中...' : 'プレミアムを始める'}
            </Button>
          ) : (
            <Button disabled variant="outline" className="w-full">
              現在利用中
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// ========================================
// ローディング用スケルトン
// ========================================

function BillingPlanPageSkeleton() {
  return (
    <div className="mx-auto w-full max-w-6xl p-6 space-y-8">
      {/* ヘッダースケルトン */}
      <div className="text-center space-y-4">
        <Skeleton className="h-10 w-48 mx-auto" />
        <Skeleton className="h-6 w-80 mx-auto" />
        <Skeleton className="h-6 w-32 mx-auto" />
      </div>

      {/* アラートスケルトン */}
      <Skeleton className="h-24 w-full" />

      {/* プランカードスケルトン */}
      <div className="grid gap-6 md:grid-cols-2">
        {[1, 2].map((i) => (
          <Card key={i}>
            <CardHeader className="text-center pb-4">
              <Skeleton className="h-6 w-32 mx-auto" />
              <Skeleton className="h-10 w-24 mx-auto" />
              <Skeleton className="h-4 w-48 mx-auto" />
            </CardHeader>
            <CardContent className="space-y-4">
              {[1, 2, 3, 4].map((j) => (
                <div key={j} className="flex items-center gap-3">
                  <Skeleton className="h-4 w-4 rounded-full" />
                  <Skeleton className="h-4 flex-1" />
                </div>
              ))}
              <Skeleton className="h-10 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>

      <Skeleton className="h-16 w-full" />
    </div>
  );
}