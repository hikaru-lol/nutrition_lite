'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LoadingState } from '@/shared/ui/Status/LoadingState';
import { ErrorState } from '@/shared/ui/Status/ErrorState';
import { Clock, Utensils, Sparkles, AlertCircle, CheckCircle, Crown, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';

import { useMealRecommendationModel } from '../model/useMealRecommendationModel';
import { MealRecommendationCooldownError, MealRecommendationDailyLimitError } from '../contract/mealRecommendationContract';

// =============================================================================
// 型定義
// =============================================================================

export interface MealRecommendationCardProps {
  date: string; // YYYY-MM-DD
  className?: string;
  onViewDetails?: () => void;
}

// =============================================================================
// コンポーネント
// =============================================================================

export function MealRecommendationCard({
  date,
  className,
  onViewDetails
}: MealRecommendationCardProps) {
  const model = useMealRecommendationModel({ date });
  const { cardState, generate, refresh, planLimit, currentCount } = model;

  // ローディング状態
  if (cardState.status === 'loading') {
    return (
      <Card className={cn('', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Utensils className="h-5 w-5" />
            食事提案
          </CardTitle>
        </CardHeader>
        <CardContent>
          <LoadingState />
        </CardContent>
      </Card>
    );
  }

  // エラー状態
  if (cardState.status === 'error') {
    return (
      <Card className={cn('', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Utensils className="h-5 w-5" />
            食事提案
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ErrorState
            title="提案の取得に失敗しました"
            message={cardState.error?.message || '不明なエラーが発生しました'}
            onRetry={refresh}
          />
        </CardContent>
      </Card>
    );
  }

  // 制限中状態
  if (cardState.status === 'rate-limited') {
    const error = cardState.error;
    const isCooldown = error instanceof MealRecommendationCooldownError;
    const isDailyLimit = error instanceof MealRecommendationDailyLimitError;

    return (
      <Card className={cn('', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Utensils className="h-5 w-5" />
            食事提案
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start gap-3 p-4 bg-amber-50 dark:bg-amber-950 rounded-lg border border-amber-200 dark:border-amber-800">
            <AlertCircle className="h-5 w-5 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" />
            <div className="space-y-2">
              {isCooldown && (
                <>
                  <div className="font-medium text-amber-800 dark:text-amber-200">
                    提案生成には時間間隔があります
                  </div>
                  <div className="text-sm text-amber-700 dark:text-amber-300">
                    あと {(error as MealRecommendationCooldownError).minutes} 分後に再生成できます
                  </div>
                  {cardState.nextGenerationTime && (
                    <div className="flex items-center gap-1 text-xs text-amber-600 dark:text-amber-400">
                      <Clock className="h-3 w-3" />
                      {cardState.nextGenerationTime.toLocaleTimeString('ja-JP', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })} 以降に生成可能
                    </div>
                  )}
                </>
              )}
              {isDailyLimit && (
                <>
                  <div className="font-medium text-amber-800 dark:text-amber-200">
                    本日の生成上限に達しました
                  </div>
                  <div className="text-sm text-amber-700 dark:text-amber-300">
                    {(error as MealRecommendationDailyLimitError).currentCount}/
                    {(error as MealRecommendationDailyLimitError).limit} 回生成済み
                  </div>
                  <div className="text-xs text-amber-600 dark:text-amber-400">
                    明日の00:00にリセットされます
                  </div>
                </>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // 未生成状態
  if (cardState.status === 'empty') {
    // フリープランで制限に達している場合のアップグレード促進
    if (planLimit.requiresUpgrade) {
      return (
        <Card className={cn('', className)}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Utensils className="h-5 w-5" />
              食事提案
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center py-6">
              <Crown className="h-12 w-12 text-amber-500 mx-auto mb-3" />
              <div className="font-medium text-foreground mb-2">
                月の提案回数の上限に達しました
              </div>
              <div className="text-sm text-muted-foreground mb-2">
                今月は{planLimit.remaining}回/{planLimit.limit}回の提案を生成しました
              </div>
              <div className="text-sm text-muted-foreground mb-4">
                プレミアムプランなら無制限で利用できます
              </div>
              <Button
                onClick={() => window.location.href = '/billing/plan'}
                className="gap-2"
              >
                <Crown className="h-4 w-4" />
                プレミアムプランを見る
              </Button>
            </div>
          </CardContent>
        </Card>
      );
    }

    return (
      <Card className={cn('', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Utensils className="h-5 w-5" />
            食事提案
            {planLimit.limit !== null && (
              <span className="ml-auto text-xs text-muted-foreground">
                {currentCount}/{planLimit.limit}
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center py-6">
            <Sparkles className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <div className="font-medium text-foreground mb-2">
              今日の食事提案を生成しましょう
            </div>
            <div className="text-sm text-muted-foreground mb-4">
              最近の栄養記録から、あなたに最適な献立を提案します
            </div>
            {planLimit.limit !== null && planLimit.remaining !== null && (
              <div className="text-xs text-muted-foreground mb-3">
                今月あと {planLimit.remaining} 回生成できます
              </div>
            )}
            <Button
              onClick={() => generate()}
              className="gap-2"
              disabled={!cardState.canGenerate}
            >
              <Sparkles className="h-4 w-4" />
              提案を生成する
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // 生成済み状態
  if (cardState.status === 'available' && cardState.recommendation) {
    const { recommendation } = cardState;
    const hasRecommendedMeals = recommendation.recommended_meals && recommendation.recommended_meals.length > 0;

    return (
      <Card className={cn('', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            食事提案
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 生成日時表示 */}
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            {new Date(recommendation.created_at).toLocaleString('ja-JP')} に生成
          </div>

          {/* 献立プレビュー */}
          {hasRecommendedMeals && (
            <div className="space-y-3">
              <div className="font-medium text-sm">おすすめ献立</div>
              <div className="grid gap-2">
                {recommendation.recommended_meals.slice(0, 3).map((meal, index) => (
                  <div
                    key={index}
                    className="p-3 bg-muted/50 rounded-lg border"
                  >
                    <div className="font-medium text-sm mb-1">{meal.title}</div>
                    <div className="text-xs text-muted-foreground mb-2">
                      {meal.description}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {meal.ingredients.slice(0, 3).map((ingredient, idx) => (
                        <span
                          key={idx}
                          className="inline-block px-2 py-0.5 bg-background rounded text-xs"
                        >
                          {ingredient}
                        </span>
                      ))}
                      {meal.ingredients.length > 3 && (
                        <span className="text-xs text-muted-foreground">
                          +{meal.ingredients.length - 3}個
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* アドバイスプレビュー */}
          {recommendation.body && (
            <div className="space-y-2">
              <div className="font-medium text-sm">栄養アドバイス</div>
              <div className="text-sm text-muted-foreground line-clamp-3">
                {recommendation.body}
              </div>
            </div>
          )}

          {/* アクションボタン */}
          <div className="flex gap-2 pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={onViewDetails}
              className="flex-1"
            >
              詳細を見る
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => generate()}
              disabled={!cardState.canGenerate || planLimit.requiresUpgrade}
              title={planLimit.requiresUpgrade ? '月の制限に達しています' : undefined}
            >
              再生成
            </Button>
          </div>

          {/* フリープランの制限表示 */}
          {planLimit.limit !== null && (
            <div className="text-xs text-muted-foreground text-center pt-2">
              今月 {currentCount}/{planLimit.limit} 回利用
              {planLimit.remaining !== null && planLimit.remaining <= 2 && (
                <span className="text-amber-600 dark:text-amber-400 ml-2">
                  あと{planLimit.remaining}回で上限です
                </span>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  // フォールバック
  return null;
}