'use client';

import { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  CheckCircle,
  Crown,
  Sparkles,
  ArrowRight,
  Gift,
  Info
} from 'lucide-react';
import { useBillingPageModel } from '../model/useBillingPageModel';

export function BillingSuccessPage() {
  const { handlePaymentSuccess, refreshPlanInfo } = useBillingPageModel();

  useEffect(() => {
    // ページ読み込み時に決済完了処理を実行
    handlePaymentSuccess();

    // プラン情報も再取得（Webhook処理の完了を待つ）
    const timer = setTimeout(() => {
      refreshPlanInfo();
    }, 2000);

    return () => clearTimeout(timer);
  }, [handlePaymentSuccess, refreshPlanInfo]);

  return (
    <div className="mx-auto w-full max-w-2xl p-6">
      {/* 成功メッセージカード */}
      <Card className="text-center border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950">
        <CardHeader className="pb-4">
          <div className="flex justify-center mb-4">
            <div className="relative">
              <CheckCircle className="h-20 w-20 text-green-500" />
              <Sparkles className="h-8 w-8 text-yellow-500 absolute -top-2 -right-2 animate-pulse" />
            </div>
          </div>
          <CardTitle className="text-2xl text-green-700 dark:text-green-300">
            🎉 プレミアムプランへようこそ！
          </CardTitle>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="space-y-4">
            <p className="text-green-600 dark:text-green-400">
              プレミアムプランのアップグレードが完了しました
            </p>

            {/* プレミアム機能紹介 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 space-y-3">
              <h3 className="font-semibold flex items-center gap-2">
                <Crown className="h-5 w-5 text-yellow-500" />
                新しく利用できる機能
              </h3>
              <div className="grid gap-2 text-sm text-left">
                <div className="flex items-center gap-3">
                  <Gift className="h-4 w-4 text-primary flex-shrink-0" />
                  <span>無制限の食事提案</span>
                </div>
                <div className="flex items-center gap-3">
                  <Gift className="h-4 w-4 text-primary flex-shrink-0" />
                  <span>詳細な栄養解析</span>
                </div>
                <div className="flex items-center gap-3">
                  <Gift className="h-4 w-4 text-primary flex-shrink-0" />
                  <span>AI栄養アドバイス（フル機能）</span>
                </div>
                <div className="flex items-center gap-3">
                  <Gift className="h-4 w-4 text-primary flex-shrink-0" />
                  <span>カスタム目標提案</span>
                </div>
                <div className="flex items-center gap-3">
                  <Gift className="h-4 w-4 text-primary flex-shrink-0" />
                  <span>詳細レポート・エクスポート機能</span>
                </div>
              </div>
            </div>

            {/* ダッシュボードへのボタン */}
            <Button
              size="lg"
              className="w-full gap-2"
              onClick={() => window.location.href = '/today'}
            >
              <ArrowRight className="h-4 w-4" />
              ダッシュボードで機能を試す
            </Button>
          </div>

          {/* β版情報 */}
          <Alert className="text-left">
            <Info className="h-4 w-4" />
            <AlertDescription className="text-sm">
              <strong>テスト環境での決済完了</strong><br />
              現在はβ版のため、実際の課金処理は発生していません。
              すべてのプレミアム機能をお試しいただけます。
            </AlertDescription>
          </Alert>

          {/* 追加情報 */}
          <div className="text-xs text-muted-foreground space-y-2">
            <p>
              課金の管理や解約は、マイページの「課金管理」から行えます。
            </p>
            <p>
              ご不明な点がございましたら、お気軽にサポートまでお問い合わせください。
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}