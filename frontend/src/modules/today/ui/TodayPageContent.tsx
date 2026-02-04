'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

import { LoadingState } from '@/shared/ui/Status/LoadingState';
import { ErrorState } from '@/shared/ui/Status/ErrorState';
import { DailySummaryCard } from '@/shared/ui/cards/DailySummaryCard';
import { CompactMealList, type MealItem } from '@/shared/ui/lists/CompactMealList';
import { AddMealModal, type AddMealFormValues } from '@/shared/ui/forms/AddMealModal';
import { EditMealModal, type EditMealFormValues, type MealItemForEdit } from '@/shared/ui/forms/EditMealModal';
import { NutritionAnalysisCard } from '@/shared/ui/cards/NutritionAnalysisCard';
import { DailyReportCard } from '@/shared/ui/cards/DailyReportCard';
import { EnhancedDailyReportCard } from '@/shared/ui/cards/EnhancedDailyReportCard';
import { MealRecommendationCard, MealRecommendationDetailModal, useMealRecommendationModel } from '@/modules/meal-recommendation';

import {
  useTodayPageModel,
  type TodayMealItemFormValues,
} from '../model/useTodayPageModel';
import { useUpdateMealItem } from '@/modules/meal/model/mealHooks';

interface TodayPageContentProps {
  date: string; // YYYY-MM-DD format
}

export function TodayPageContent({ date }: TodayPageContentProps) {
  const router = useRouter();
  const m = useTodayPageModel({ date });
  const updateMutation = useUpdateMealItem(date);
  const mealRecommendationModel = useMealRecommendationModel({ date });

  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedMealType, setSelectedMealType] = useState<'main' | 'snack'>('main');
  const [selectedMealIndex, setSelectedMealIndex] = useState<number>(1);
  const [editingMealItem, setEditingMealItem] = useState<MealItemForEdit | null>(null);
  const [showNutritionDetailsModal, setShowNutritionDetailsModal] = useState(false);
  const [nutritionDetailsData, setNutritionDetailsData] = useState<any>(null);
  const [showMealRecommendationModal, setShowMealRecommendationModal] = useState(false);
  const [selectedRecommendation, setSelectedRecommendation] = useState<any>(null);

  const handleAddClick = (mealType: 'main' | 'snack', mealIndex?: number) => {
    setSelectedMealType(mealType);
    if (mealType === 'main' && mealIndex) {
      setSelectedMealIndex(mealIndex);
    }
    setIsAddModalOpen(true);
  };

  const handleAddModalSubmit = async (values: AddMealFormValues) => {
    await m.addMealItem(values);
    setIsAddModalOpen(false);
  };

  const handleEditClick = (mealItem: MealItem) => {
    setEditingMealItem({
      id: mealItem.id,
      date: date,
      meal_type: mealItem.meal_type,
      meal_index: mealItem.meal_index,
      name: mealItem.name,
      serving_count: mealItem.serving_count,
      note: mealItem.note,
    });
    setIsEditModalOpen(true);
  };

  const handleEditModalSubmit = async (values: EditMealFormValues) => {
    if (editingMealItem) {
      await updateMutation.mutateAsync({
        entryId: editingMealItem.id,
        data: values,
      });
      setIsEditModalOpen(false);
      setEditingMealItem(null);
    }
  };

  const handleNutritionAnalysis = async (mealType: 'main' | 'snack', mealIndex?: number) => {
    // 新しいキャッシュベースの栄養分析
    try {
      const nutritionData = await m.fetchMealNutrition(mealType, mealIndex);
      // 成功した場合は自動的にキャッシュに保存される
      console.log('栄養分析完了:', nutritionData);
    } catch (error) {
      console.error('栄養分析エラー:', error);
    }

    // 既存のUI用にも設定（後で削除予定）
    m.selectMealForNutrition(mealType, mealIndex ?? null);
  };

  const handleShowNutritionDetails = (nutritionData: any) => {
    setNutritionDetailsData(nutritionData);
    setShowNutritionDetailsModal(true);
  };

  const handleShowMealRecommendationDetails = () => {
    // 現在表示されている食事提案データを取得
    const currentRecommendation = mealRecommendationModel.recommendation;
    if (currentRecommendation) {
      setSelectedRecommendation(currentRecommendation);
      setShowMealRecommendationModal(true);
    }
  };

  if (m.isLoading) return <LoadingState label="データを読み込み中..." />;
  if (m.isError)
    return (
      <ErrorState
        title="データの取得に失敗"
        message="BFF/Backend の疎通を確認してください。"
        onRetry={() => router.refresh()}
      />
    );

  const activeTarget = m.activeTargetQuery.data;
  const mealItems = m.mealItemsQuery.data?.items ?? [];
  const profile = m.profileQuery.data;
  const mealsPerDay = profile?.meals_per_day ?? 3;

  return (
    <div className="w-full space-y-6">
      {/* 本日のサマリー */}
      <div data-tour="daily-summary">
        <DailySummaryCard
          data={m.dailySummaryData}
          isLoading={m.dailySummaryQuery.isLoading}
        />
      </div>

      {/* 食事提案 */}
      <div data-tour="meal-recommendation">
        <MealRecommendationCard
          date={date}
          onViewDetails={handleShowMealRecommendationDetails}
        />
      </div>

      {/* 食事ログ（コンパクト版） */}
      <div data-tour="meal-list">
        <CompactMealList
        mealItems={mealItems.map((item) => ({
          id: item.id,
          name: item.name,
          meal_type: item.meal_type,
          meal_index: item.meal_index ?? null,
          serving_count: item.serving_count ?? null,
          note: item.note ?? null,
        }))}
        mealsPerDay={mealsPerDay}
        onDelete={m.removeMealItem}
        onEdit={handleEditClick}
        onAddClick={handleAddClick}
        onAnalyzeNutrition={handleNutritionAnalysis}
        isDeleting={m.deleteMutation.isPending}
        selectedMealForNutrition={m.selectedMealForNutrition}
        nutritionData={m.selectedMealNutritionQuery.data}
        isNutritionLoading={m.selectedMealNutritionQuery.isLoading}
        nutritionError={m.selectedMealNutritionQuery.isError}
        onClearNutritionAnalysis={m.clearSelectedMeal}
        onRefetchNutrition={() => m.selectedMealNutritionQuery.refetch()}
        onShowNutritionDetails={handleShowNutritionDetails}
        getNutritionDataFromCache={m.getMealNutritionFromCache}
      />


      {/* 目標達成度 - リッチチャート版 */}
      <div data-tour="target-progress">
        {!activeTarget ? (
          <Card>
            <CardHeader>
              <CardTitle>目標達成度</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground">
                ターゲットを設定すると達成度が表示されます。
              </div>
            </CardContent>
          </Card>
        ) : mealItems.length === 0 ? (
          <Card>
            <CardHeader>
              <CardTitle>目標達成度</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground">
                食事を追加すると達成度が表示されます。
              </div>
            </CardContent>
          </Card>
        ) : m.dailySummaryQuery.isLoading ? (
          <Card>
            <CardHeader>
              <CardTitle>目標達成度</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground">計算中...</div>
            </CardContent>
          </Card>
        ) : m.dailySummaryQuery.isError ? (
          <Card>
            <CardHeader>
              <CardTitle>目標達成度</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-destructive">
                栄養データの取得に失敗しました。
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => m.dailySummaryQuery.refetch()}
                className="mt-2"
              >
                再試行
              </Button>
            </CardContent>
          </Card>
        ) : m.nutrientProgress.length > 0 ? (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>目標達成度</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-8">
                  {(() => {
                    const categories = {
                      macronutrients: {
                        title: '主要栄養素 (PFC)',
                        icon: '🥩',
                        nutrients: ['protein', 'fat', 'carbohydrate']
                      },
                      minerals: {
                        title: 'ミネラル',
                        icon: '💧',
                        nutrients: ['sodium', 'potassium', 'iron', 'calcium']
                      },
                      vitamins_others: {
                        title: 'ビタミン・その他',
                        icon: '💊',
                        nutrients: ['vitamin_d', 'water', 'fiber']
                      }
                    };

                    return Object.entries(categories).map(([categoryKey, category]) => {
                      const categoryNutrients = m.nutrientProgress.filter(np =>
                        category.nutrients.includes(np.code)
                      );

                      if (categoryNutrients.length === 0) return null;

                      return (
                        <div key={categoryKey} className="mb-8 last:mb-0">
                          <div className="flex items-center gap-3 pb-3 mb-4 border-b-2 border-gray-200 dark:border-gray-600">
                            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-700">
                              <span className="text-lg">{category.icon}</span>
                            </div>
                            <h3 className="text-base font-bold text-gray-800 dark:text-gray-200 uppercase tracking-wide">
                              {category.title}
                            </h3>
                          </div>

                          <div className="space-y-2">
                            {categoryNutrients.map((np) => (
                              <div key={np.code} className="grid grid-cols-[90px_1fr_110px] gap-4 items-center">
                                <div className="text-sm font-medium text-gray-900 dark:text-gray-300 truncate">
                                  {np.label}
                                </div>

                                <div className="h-3 w-full bg-gray-200 dark:bg-gray-700 rounded-full">
                                  <div
                                    className={`h-3 rounded-full transition-all duration-300 ${
                                      np.percentage > 100 ? 'bg-red-500' :
                                      np.percentage >= 80 ? 'bg-green-500' :
                                      'bg-blue-500'
                                    }`}
                                    style={{ width: `${Math.min(np.percentage, 100)}%` }}
                                  />
                                </div>

                                <div className="text-right">
                                  <div className="text-sm font-bold text-gray-900 dark:text-white">
                                    {np.percentage.toFixed(0)}%
                                  </div>
                                  <div className="text-xs text-gray-500 dark:text-gray-400 font-mono">
                                    {np.actual.toFixed(1)}/{np.target.toFixed(1)}{np.unit}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    });
                  })()}
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>目標達成度</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground">
                栄養データを処理中です。しばらくお待ちください。
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Enhanced Daily Report */}
      <div data-tour="daily-report">
        {m.dailyReport ? (
          <EnhancedDailyReportCard
            report={m.dailyReport}
            isLoading={m.dailyReportQuery.isLoading}
            onShare={() => {
              console.log('Share report functionality');
            }}
            onExport={() => {
              console.log('Export report functionality');
            }}
          />
        ) : (
          <DailyReportCard
            date={date}
            report={m.dailyReportQuery.data}
            isLoading={m.dailyReportQuery.isLoading}
            isError={m.dailyReportQuery.isError}
            isGenerating={m.generateReportMutation.isPending}
            generateError={m.generateReportMutation.error}
            queryError={m.dailyReportQuery.error}
            isMealCompletionValid={m.isMealCompletionValid}
            mealCompletionStatus={m.getMealCompletionStatus}
            missingMealsCount={m.missingMealsCount}
            hasEnoughData={m.hasEnoughData}
            onGenerate={(targetDate) => m.generateReportMutation.mutate({ date: targetDate })}
            onFetch={(targetDate) => m.dailyReportQuery.refetch()}
          />
        )}
      </div>

      {/* 食事追加モーダル */}
      <AddMealModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSubmit={handleAddModalSubmit}
        mealType={selectedMealType}
        mealIndex={selectedMealIndex}
        date={date}
        isLoading={m.createMutation.isPending}
        error={m.createMutation.isError
          ? '追加に失敗しました。/meal-items エンドポイントを確認してください。'
          : null
        }
      />

      {/* 食事編集モーダル */}
      <EditMealModal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setEditingMealItem(null);
        }}
        onSubmit={handleEditModalSubmit}
        mealItem={editingMealItem}
        isLoading={updateMutation.isPending}
        error={updateMutation.isError
          ? '更新に失敗しました。/meal-items/{id} エンドポイントを確認してください。'
          : null
        }
      />

      {/* エラー表示 */}
      {m.deleteMutation.isError && (
        <div className="text-sm text-destructive">
          削除に失敗しました。/meal-items/{'{id}'} を確認してください。
        </div>
      )}

      {/* 栄養分析詳細モーダル */}
      {showNutritionDetailsModal && nutritionDetailsData && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-900 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-auto">
            <NutritionAnalysisCard
              mealData={nutritionDetailsData.meal}
              dailyData={nutritionDetailsData.daily}
              onClose={() => {
                setShowNutritionDetailsModal(false);
                setNutritionDetailsData(null);
              }}
              isLoading={false}
            />
          </div>
        </div>
      )}

      {/* 食事提案詳細モーダル */}
      <MealRecommendationDetailModal
        recommendation={selectedRecommendation}
        isOpen={showMealRecommendationModal}
        onClose={() => {
          setShowMealRecommendationModal(false);
          setSelectedRecommendation(null);
        }}
        onShare={() => {
          // TODO: 共有機能実装
          console.log('Share recommendation');
        }}
        onFavorite={() => {
          // TODO: お気に入り機能実装
          console.log('Favorite recommendation');
        }}
        onExport={() => {
          // TODO: エクスポート機能実装
          console.log('Export recommendation');
        }}
      />
    </div>
    </div>
  );
}