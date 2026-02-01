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
import { EnhancedDailyReportCard } from '@/shared/ui/cards/EnhancedDailyReportCard';

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

  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedMealType, setSelectedMealType] = useState<'main' | 'snack'>('main');
  const [selectedMealIndex, setSelectedMealIndex] = useState<number>(1);
  const [editingMealItem, setEditingMealItem] = useState<MealItemForEdit | null>(null);

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

  const handleNutritionAnalysis = (mealType: 'main' | 'snack', mealIndex?: number) => {
    m.selectMealForNutrition(mealType, mealIndex ?? null);
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
      <DailySummaryCard
        data={m.dailySummaryData}
        isLoading={m.dailySummaryQuery.isLoading}
      />

      {/* 食事ログ（コンパクト版） */}
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
      />

      {/* 栄養分析セクション */}
      {m.selectedMealForNutrition && (
        <div>
          {m.selectedMealNutritionQuery.isLoading && (
            <Card>
              <CardHeader>
                <CardTitle>栄養分析</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground">計算中...</div>
              </CardContent>
            </Card>
          )}

          {m.selectedMealNutritionQuery.data && (
            <NutritionAnalysisCard
              mealData={m.selectedMealNutritionQuery.data.meal}
              dailyData={m.selectedMealNutritionQuery.data.daily}
              onClose={m.clearSelectedMeal}
              isLoading={false}
            />
          )}
        </div>
      )}

      {/* 栄養分析エラー表示 */}
      {m.selectedMealForNutrition && m.selectedMealNutritionQuery.isError && (
        <Card>
          <CardHeader>
            <CardTitle>栄養分析エラー</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-destructive">
              栄養分析の取得に失敗しました。
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => m.selectedMealNutritionQuery.refetch()}
              className="mt-2"
            >
              再試行
            </Button>
          </CardContent>
        </Card>
      )}

      {/* 目標達成度 - リッチチャート版 */}
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

      {/* Enhanced Daily Report */}
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
        <Card>
          <CardHeader>
            <CardTitle>日次レポート</CardTitle>
          </CardHeader>
          <CardContent>
            {m.dailyReportQuery.isLoading ? (
              <div className="text-sm text-muted-foreground">読み込み中...</div>
            ) : (
              <div className="space-y-3">
                <div className="text-sm text-muted-foreground">
                  日次レポートがまだ生成されていません。
                </div>
                <Button
                  onClick={() => m.generateReportMutation.mutate()}
                  disabled={m.generateReportMutation.isPending}
                >
                  {m.generateReportMutation.isPending
                    ? 'レポート生成中...'
                    : 'レポートを生成する'}
                </Button>
                {m.generateReportMutation.isError ? (
                  <div className="text-sm text-destructive">
                    レポート生成に失敗しました。食事ログが完了しているか確認してください。
                  </div>
                ) : null}
              </div>
            )}
          </CardContent>
        </Card>
      )}

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
    </div>
  );
}