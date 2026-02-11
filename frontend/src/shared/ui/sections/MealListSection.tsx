/**
 * MealListSection - Layer 1: UI Presentation
 *
 * 責務:
 * - 純粋な食事リスト表現
 * - propsによる制御のみ
 * - 副作用なし
 */

'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Utensils, Cookie } from 'lucide-react';
import type { MealItem } from '@/modules/meal/contract/mealContract';
import { groupMealsByType, type GroupedMeals } from '@/modules/meal/lib/groupMeals';



// ========================================
// Types
// ========================================

export interface MealListSectionProps {
  // Data
  mealItems: readonly MealItem[];
  mealsPerDay: number;

  // State
  isLoading: boolean;
  isDeleting: boolean;

  // Actions
  onAddMeal: (type: 'main' | 'snack', index?: number) => void;
  onEditMeal: (item: MealItem) => void;
  onDeleteMeal: (id: string) => void;
  onAnalyzeNutrition: (type: 'main' | 'snack', index?: number) => void;

  // Nutrition analysis (統一インターフェース)
  nutritionAnalysis: {
    selectedMeal: { meal_type: 'main' | 'snack'; meal_index: number | null } | null;
    data: any | null;
    isLoading: boolean;
    nutritionDataAvailability: Map<string, boolean>;
    onShowDetails: (mealType: 'main' | 'snack', mealIndex?: number) => void;
    onClear: () => void;
  };
}

// ========================================
// Component
// ========================================

export const MealListSection = React.memo(function MealListSection({
  mealItems,
  mealsPerDay,
  isLoading,
  isDeleting,
  onAddMeal,
  onEditMeal,
  onDeleteMeal,
  onAnalyzeNutrition,
  nutritionAnalysis,
}: MealListSectionProps) {

  // ========================================
  // Computed Data
  // ========================================

  const groupedMeals = groupMealsByType(mealItems, mealsPerDay);

  // ========================================
  // Loading State
  // ========================================

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Utensils className="h-5 w-5" />
            今日の食事
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="animate-pulse space-y-3">
            {Array.from({ length: mealsPerDay + 1 }).map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded-md" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  // ========================================
  // Main Render
  // ========================================

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Utensils className="h-5 w-5" />
          今日の食事
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">

        {/* メイン食事セクション */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-muted-foreground">メイン食事</h3>
          <div className="grid gap-3">
            {groupedMeals.main.map(({ index, items }) => (
              <MealIndexSection
                key={`main-${index}`}
                title={`食事 ${index}`}
                mealType="main"
                mealIndex={index}
                items={items}
                onAdd={() => onAddMeal('main', index)}
                onEdit={onEditMeal}
                onDelete={onDeleteMeal}
                onAnalyze={() => onAnalyzeNutrition('main', index)}
                isDeleting={isDeleting}
                nutritionAnalysis={nutritionAnalysis}
              />
            ))}
          </div>
        </div>

        {/* 間食セクション */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <Cookie className="h-4 w-4" />
            間食
          </h3>
          <MealIndexSection
            title="間食"
            mealType="snack"
            mealIndex={null}
            items={groupedMeals.snacks}
            onAdd={() => onAddMeal('snack')}
            onEdit={onEditMeal}
            onDelete={onDeleteMeal}
            onAnalyze={() => onAnalyzeNutrition('snack')}
            isDeleting={isDeleting}
            nutritionAnalysis={nutritionAnalysis}
          />
        </div>

      </CardContent>
    </Card>
  );
});

// ========================================
// Sub Components
// ========================================

interface MealIndexSectionProps {
  title: string;
  mealType: 'main' | 'snack';
  mealIndex: number | null;
  items: MealItem[];
  onAdd: () => void;
  onEdit: (item: MealItem) => void;
  onDelete: (id: string) => void;
  onAnalyze: () => void;
  isDeleting: boolean;
  // 栄養分析（統一インターフェース）
  nutritionAnalysis: {
    selectedMeal: { meal_type: 'main' | 'snack'; meal_index: number | null } | null;
    data: any | null;
    isLoading: boolean;
    nutritionDataAvailability: Map<string, boolean>;
    onShowDetails: (mealType: 'main' | 'snack', mealIndex?: number) => void;
    onClear: () => void;
  };
}

const MealIndexSection = React.memo(function MealIndexSection({
  title,
  mealType,
  mealIndex,
  items,
  onAdd,
  onEdit,
  onDelete,
  onAnalyze,
  isDeleting,
  nutritionAnalysis,
}: MealIndexSectionProps) {
  const hasItems = items.length > 0;

  // Layer 1: propsから栄養データの有無を取得（純粋な表現）
  const sectionKey = mealType === 'main' ? `main-${mealIndex}` : 'snack';
  const hasNutritionData = nutritionAnalysis.nutritionDataAvailability.get(sectionKey) ?? false;

  return (
    <div className="border border-border rounded-lg p-4 space-y-3">

      {/* セクションヘッダー */}
      <div className="flex items-center justify-between">
        <h4 className="font-medium">{title}</h4>
        <div className="flex items-center gap-2">
          {hasItems && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={onAnalyze}
                disabled={nutritionAnalysis.isLoading}
              >
                栄養分析
              </Button>
              {hasNutritionData && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => nutritionAnalysis.onShowDetails(mealType, mealIndex ?? undefined)}
                  className="flex items-center gap-1"
                >
                  詳細表示
                </Button>
              )}
            </>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={onAdd}
            className="flex items-center gap-1"
          >
            <Plus className="h-3 w-3" />
            追加
          </Button>
        </div>
      </div>

      {/* 食事アイテム一覧 */}
      {hasItems ? (
        <div className="space-y-2">
          {items.map(item => (
            <MealItemCard
              key={item.id}
              item={item}
              onEdit={onEdit}
              onDelete={onDelete}
              isDeleting={isDeleting}
            />
          ))}
        </div>
      ) : (
        <div className="text-sm text-muted-foreground text-center py-8">
          まだ食事が記録されていません
        </div>
      )}

    </div>
  );
});

// ========================================
// Meal Item Card
// ========================================

interface MealItemCardProps {
  item: MealItem;
  onEdit: (item: MealItem) => void;
  onDelete: (id: string) => void;
  isDeleting: boolean;
}

const MealItemCard = React.memo(function MealItemCard({
  item,
  onEdit,
  onDelete,
  isDeleting
}: MealItemCardProps) {
  return (
    <div className="flex items-center justify-between p-2 border rounded bg-background">
      <div className="flex-1 min-w-0">
        <div className="font-medium truncate">{item.name}</div>
        {item.serving_count && (
          <div className="text-sm text-muted-foreground">
            {item.serving_count} 人前
          </div>
        )}
        {item.note && (
          <div className="text-xs text-muted-foreground truncate">
            {item.note}
          </div>
        )}
      </div>
      <div className="flex gap-1 ml-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onEdit(item)}
        >
          編集
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onDelete(item.id)}
          disabled={isDeleting}
          className="text-destructive hover:text-destructive"
        >
          削除
        </Button>
      </div>
    </div>
  );
});