'use client';

import { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  XCircle,
  ArrowLeft,
  RefreshCw,
  Heart,
  MessageCircle,
  Info
} from 'lucide-react';
import { useBillingPageModel } from '../model/useBillingPageModel';

export function BillingCancelPage() {
  const { handlePaymentCancel, startCheckout, isCheckoutPending } = useBillingPageModel();

  useEffect(() => {
    // ページ読み込み時にキャンセル処理を実行
    handlePaymentCancel();
  }, [handlePaymentCancel]);

  return (
    <div className="mx-auto w-full max-w-2xl p-6">
      {/* キャンセルメッセージカード */}
      <Card className="text-center border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950">
        <CardHeader className="pb-4">
          <div className="flex justify-center mb-4">
            <XCircle className="h-16 w-16 text-yellow-500" />
          </div>
          <CardTitle className="text-xl text-yellow-700 dark:text-yellow-300">
            決済がキャンセルされました
          </CardTitle>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="space-y-4">
            <p className="text-yellow-600 dark:text-yellow-400">
              プレミアムプランへのアップグレードをキャンセルしました。
              いつでも再度お試しいただけます。
            </p>

            {/* アクションボタン */}
            <div className="space-y-3">
              <Button
                size="lg"
                className="w-full gap-2"
                onClick={() => startCheckout()}
                disabled={isCheckoutPending}
              >
                <RefreshCw className="h-4 w-4" />
                {isCheckoutPending ? '処理中...' : 'もう一度プレミアムを試す'}
              </Button>

              <Button
                variant="outline"
                size="lg"
                className="w-full gap-2"
                onClick={() => window.location.href = '/billing/plan'}
              >
                <ArrowLeft className="h-4 w-4" />
                プラン選択に戻る
              </Button>

              <Button
                variant="ghost"
                size="sm"
                className="w-full gap-2"
                onClick={() => window.location.href = '/today'}
              >
                ダッシュボードに戻る
              </Button>
            </div>

            {/* フリープランでも利用可能な機能 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 space-y-3">
              <h3 className="font-semibold flex items-center gap-2">
                <Heart className="h-5 w-5 text-red-500" />
                フリープランでもご利用いただけます
              </h3>
              <div className="grid gap-2 text-sm text-left">
                <div className="flex items-center gap-3">
                  <span className="w-2 h-2 bg-primary rounded-full flex-shrink-0" />
                  <span>食事記録の登録・管理</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-2 h-2 bg-primary rounded-full flex-shrink-0" />
                  <span>基本的な栄養データ表示</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-2 h-2 bg-primary rounded-full flex-shrink-0" />
                  <span>月間サマリー</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-2 h-2 bg-primary rounded-full flex-shrink-0" />
                  <span>食事提案（月5回まで）</span>
                </div>
              </div>
            </div>

            {/* β版情報 */}
            <Alert className="text-left">
              <Info className="h-4 w-4" />
              <AlertDescription className="text-sm">
                <strong>テスト環境について</strong><br />
                現在はβ版のため、実際の課金処理は発生しません。
                プレミアム機能をいつでもお試しいただけます。
              </AlertDescription>
            </Alert>

            {/* フィードバック促進 */}
            <div className="bg-blue-50 dark:bg-blue-950 rounded-lg p-4 space-y-3">
              <h3 className="font-semibold flex items-center gap-2 text-blue-700 dark:text-blue-300">
                <MessageCircle className="h-4 w-4" />
                ご意見をお聞かせください
              </h3>
              <p className="text-sm text-blue-600 dark:text-blue-400">
                プレミアムプランについてご不明な点や、
                追加してほしい機能がございましたら、お気軽にお知らせください。
              </p>
              <Button variant="outline" size="sm" className="text-xs">
                フィードバックを送る
              </Button>
            </div>

            {/* 追加情報 */}
            <div className="text-xs text-muted-foreground">
              <p>
                決済でご不明な点がございましたら、サポートまでお問い合わせください。
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}