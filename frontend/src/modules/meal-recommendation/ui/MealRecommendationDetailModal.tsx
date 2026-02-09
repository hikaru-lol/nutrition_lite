'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
// import { ScrollArea } from '@/components/ui/scroll-area'; // 代替実装を使用
import {
  Clock,
  Utensils,
  ChefHat,
  Lightbulb,
  Users,
  Timer,
  X,
  Share2,
  Heart,
  Download
} from 'lucide-react';

import type { MealRecommendation } from '../contract/mealRecommendationContract';
import { useMealRecommendationModel } from '../model/useMealRecommendationModel';

// =============================================================================
// 型定義
// =============================================================================

export interface MealRecommendationDetailModalProps {
  recommendation: MealRecommendation | null;
  isOpen: boolean;
  onClose: () => void;
  onShare?: () => void;
  onFavorite?: () => void;
  onExport?: () => void;
}

// =============================================================================
// コンポーネント
// =============================================================================

export function MealRecommendationDetailModal({
  recommendation,
  isOpen,
  onClose,
  onShare,
  onFavorite,
  onExport
}: MealRecommendationDetailModalProps) {
  const [showHistory, setShowHistory] = useState(false);
  const historyModel = useMealRecommendationModel({ enabled: showHistory });

  if (!recommendation) return null;

  const hasRecommendedMeals = recommendation.recommended_meals && recommendation.recommended_meals.length > 0;
  const generatedDate = new Date(recommendation.created_at);
  const forDate = new Date(recommendation.generated_for_date);

  const handleShowHistory = () => {
    setShowHistory(true);
    historyModel.actions.loadHistory();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden p-0">
        <DialogHeader className="p-6 pb-4 border-b">
          <div className="flex items-start justify-between">
            <div>
              <DialogTitle className="text-2xl font-bold flex items-center gap-3">
                <ChefHat className="h-6 w-6 text-primary" />
                食事提案詳細
              </DialogTitle>
              <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  {forDate.toLocaleDateString('ja-JP')} の提案
                </div>
                <div className="flex items-center gap-1">
                  <Timer className="h-4 w-4" />
                  {generatedDate.toLocaleString('ja-JP')} に生成
                </div>
              </div>
            </div>

            {/* アクションボタン */}
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleShowHistory}
                disabled={showHistory}
              >
                <Clock className="h-4 w-4 mr-1" />
                履歴
              </Button>
              {onShare && (
                <Button variant="ghost" size="sm" onClick={onShare}>
                  <Share2 className="h-4 w-4" />
                </Button>
              )}
              {onFavorite && (
                <Button variant="ghost" size="sm" onClick={onFavorite}>
                  <Heart className="h-4 w-4" />
                </Button>
              )}
              {onExport && (
                <Button variant="ghost" size="sm" onClick={onExport}>
                  <Download className="h-4 w-4" />
                </Button>
              )}
              <Button variant="ghost" size="sm" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </DialogHeader>

        <div className="flex-1 p-6 overflow-y-auto max-h-[60vh]">
          <div className="space-y-6">
            {/* おすすめ献立セクション */}
            {hasRecommendedMeals && (
              <section>
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Utensils className="h-5 w-5" />
                  おすすめ献立 ({recommendation.recommended_meals.length}品)
                </h3>
                <div className="grid gap-4 md:grid-cols-2">
                  {recommendation.recommended_meals.map((meal, index) => (
                    <Card key={index} className="overflow-hidden">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg">{meal.title}</CardTitle>
                        <Badge variant="secondary" className="w-fit">
                          {meal.nutrition_focus}
                        </Badge>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <p className="text-sm text-muted-foreground leading-relaxed">
                          {meal.description}
                        </p>

                        <div>
                          <h5 className="font-medium text-sm mb-2 flex items-center gap-1">
                            <Users className="h-3 w-3" />
                            使用食材
                          </h5>
                          <div className="flex flex-wrap gap-1">
                            {meal.ingredients.map((ingredient, idx) => (
                              <Badge
                                key={idx}
                                variant="outline"
                                className="text-xs"
                              >
                                {ingredient}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </section>
            )}

            {/* 栄養アドバイスセクション */}
            {recommendation.body && (
              <section>
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Lightbulb className="h-5 w-5" />
                  栄養アドバイス
                </h3>
                <Card>
                  <CardContent className="p-4">
                    <div className="prose prose-sm max-w-none dark:prose-invert">
                      <p className="whitespace-pre-wrap leading-relaxed text-foreground">
                        {recommendation.body}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </section>
            )}

            {/* 実践のコツセクション */}
            {recommendation.tips && recommendation.tips.length > 0 && (
              <section>
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Lightbulb className="h-5 w-5" />
                  実践のコツ
                </h3>
                <Card>
                  <CardContent className="p-4">
                    <ul className="space-y-3">
                      {recommendation.tips.map((tip, index) => (
                        <li key={index} className="flex items-start gap-3">
                          <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-xs font-medium text-primary">
                              {index + 1}
                            </span>
                          </div>
                          <p className="text-sm leading-relaxed text-foreground">
                            {tip}
                          </p>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </section>
            )}

            {/* 履歴セクション */}
            {showHistory && (
              <section>
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  提案履歴
                </h3>
                {historyModel.state.isLoadingHistory ? (
                  <Card>
                    <CardContent className="p-4">
                      <div className="text-sm text-muted-foreground">履歴を読み込み中...</div>
                    </CardContent>
                  </Card>
                ) : historyModel.data.recommendations && historyModel.data.recommendations.length > 0 ? (
                  <div className="space-y-3">
                    {historyModel.data.recommendations.slice(0, 5).map((historyRec) => {
                      const historyDate = new Date(historyRec.created_at);
                      const historyForDate = new Date(historyRec.generated_for_date);
                      return (
                        <Card key={historyRec.id} className="overflow-hidden">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-start mb-2">
                              <div className="text-sm font-medium">
                                {historyForDate.toLocaleDateString('ja-JP')} の提案
                              </div>
                              <div className="text-xs text-muted-foreground">
                                {historyDate.toLocaleDateString('ja-JP')}
                              </div>
                            </div>
                            {historyRec.recommended_meals && historyRec.recommended_meals.length > 0 && (
                              <div className="text-sm text-muted-foreground">
                                {historyRec.recommended_meals.slice(0, 2).map(meal => meal.title).join(', ')}
                                {historyRec.recommended_meals.length > 2 && ' など'}
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      );
                    })}
                    {historyModel.data.recommendations.length > 5 && (
                      <div className="text-center text-sm text-muted-foreground">
                        他 {historyModel.data.recommendations.length - 5} 件の履歴があります
                      </div>
                    )}
                  </div>
                ) : (
                  <Card>
                    <CardContent className="p-4">
                      <div className="text-sm text-muted-foreground">履歴がありません</div>
                    </CardContent>
                  </Card>
                )}
              </section>
            )}

            {/* メタ情報 */}
            <section className="pt-4 border-t">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-muted-foreground">提案ID:</span>
                  <span className="ml-2 font-mono text-xs">{recommendation.id}</span>
                </div>
                <div>
                  <span className="font-medium text-muted-foreground">対象日:</span>
                  <span className="ml-2">{forDate.toLocaleDateString('ja-JP')}</span>
                </div>
              </div>
            </section>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}