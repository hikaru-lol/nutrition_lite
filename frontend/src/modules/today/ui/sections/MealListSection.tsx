/**
 * MealListSection - 食事リスト表示セクション
 *
 * 責務:
 * - Context経由での食事・栄養・モーダル・プロフィールデータ取得
 * - CompactMealListコンポーネントとの統合
 * - 栄養分析・モーダル連携のハンドリング
 */

'use client';

import { useCallback } from 'react';
import { CompactMealList } from '@/shared/ui/lists/CompactMealList';
import {
  useTodayMeals,
  useTodayNutrition,
  useTodayModals,
  useTodayProfile
} from '../../context/TodayPageContext';

// ========================================
// Component Interface
// ========================================

interface MealListSectionProps {
  className?: string;
}

// ========================================
// Main Component
// ========================================

export function MealListSection({ className }: MealListSectionProps = {}) {
  // Context経由で各ドメインデータを取得
  const meals = useTodayMeals();
  const nutrition = useTodayNutrition();
  const modals = useTodayModals();
  const profile = useTodayProfile();

  // ========================================
  // Event Handlers
  // ========================================

  // 食事編集ハンドラー
  const handleEditClick = useCallback((mealItem: any) => {
    modals.openEditModal({
      id: mealItem.id,
      date: mealItem.date,
      meal_type: mealItem.meal_type,
      meal_index: mealItem.meal_index,
      name: mealItem.name,
      amount_value: mealItem.amount_value,
      amount_unit: mealItem.amount_unit,
      serving_count: mealItem.serving_count,
      note: mealItem.note,
    });
  }, [modals.openEditModal]);

  // 食事追加ハンドラー
  const handleAddClick = useCallback((mealType: 'main' | 'snack', mealIndex?: number) => {
    modals.openAddModal(mealType, mealIndex);
  }, [modals.openAddModal]);

  // 栄養分析ハンドラー
  const handleNutritionAnalysis = useCallback(async (mealType: 'main' | 'snack', mealIndex?: number) => {
    try {
      // 新しいキャッシュベースの栄養分析
      const nutritionData = await nutrition.analyze(mealType, mealIndex);
      console.log('栄養分析完了:', nutritionData);

      // 既存のUI用にも設定（後で削除予定）
      nutrition.selectMeal(mealType, mealIndex ?? null);
    } catch (error) {
      console.error('栄養分析エラー:', error);
    }
  }, [nutrition.analyze, nutrition.selectMeal]);

  // 栄養詳細表示ハンドラー
  const handleShowNutritionDetails = useCallback((nutritionData: any) => {
    modals.openNutritionModal(nutritionData);
  }, [modals.openNutritionModal]);

  // 栄養分析クリアハンドラー
  const handleClearNutritionAnalysis = useCallback(() => {
    nutrition.clearSelected();
  }, [nutrition.clearSelected]);

  // 栄養分析再取得ハンドラー
  const handleRefetchNutrition = useCallback(() => {
    nutrition.refetch();
  }, [nutrition.refetch]);

  // ========================================
  // データ変換
  // ========================================

  // 食事アイテムのデータ変換
  const transformedMealItems = meals.items.map((item) => ({
    id: item.id,
    name: item.name,
    meal_type: item.meal_type,
    meal_index: item.meal_index ?? null,
    serving_count: item.serving_count ?? null,
    note: item.note ?? null,
  }));

  // ========================================
  // Render
  // ========================================

  return (
    <div className={className} data-tour="meal-list">
      <CompactMealList
        mealItems={transformedMealItems}
        mealsPerDay={profile.mealsPerDay}
        onDelete={meals.remove}
        onEdit={handleEditClick}
        onAddClick={handleAddClick}
        onAnalyzeNutrition={handleNutritionAnalysis}
        isDeleting={Object.values(meals.isDeletingMap).some(Boolean)}
        selectedMealForNutrition={nutrition.selectedMeal}
        nutritionData={nutrition.nutritionData}
        isNutritionLoading={nutrition.isLoading}
        nutritionError={nutrition.isError}
        onClearNutritionAnalysis={handleClearNutritionAnalysis}
        onRefetchNutrition={handleRefetchNutrition}
        onShowNutritionDetails={handleShowNutritionDetails}
        getNutritionDataFromCache={nutrition.getFromCache}
      />
    </div>
  );
}

// ========================================
// 軽量版・特殊用途バリエーション
// ========================================

/**
 * 食事数のみ表示する軽量版
 */
export function MealCountSection({ className }: MealListSectionProps = {}) {
  const meals = useTodayMeals();
  const profile = useTodayProfile();

  if (meals.isLoading) {
    return (
      <div className={className}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-24"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="text-sm text-muted-foreground">
        食事記録: {meals.items.length} / {profile.mealsPerDay}
      </div>
    </div>
  );
}

/**
 * 最新の食事のみ表示
 */
export function LatestMealSection({ className }: MealListSectionProps = {}) {
  const meals = useTodayMeals();

  if (meals.isLoading) {
    return (
      <div className={className}>
        <div className="animate-pulse">
          <div className="h-12 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (meals.items.length === 0) {
    return (
      <div className={className}>
        <div className="text-sm text-muted-foreground">
          まだ食事が記録されていません
        </div>
      </div>
    );
  }

  const latestMeal = meals.items[meals.items.length - 1];

  return (
    <div className={className}>
      <div className="p-3 border rounded-lg">
        <div className="text-sm font-medium">{latestMeal.name}</div>
        <div className="text-xs text-muted-foreground">
          {latestMeal.meal_type === 'main'
            ? `食事${latestMeal.meal_index}`
            : 'おやつ'
          }
        </div>
      </div>
    </div>
  );
}

// ========================================
// デバッグ用コンポーネント
// ========================================

/**
 * 食事リストデータのプレビュー（開発用）
 */
export function MealListPreview() {
  const meals = useTodayMeals();
  const nutrition = useTodayNutrition();

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <details className="p-4 border rounded-lg">
      <summary className="cursor-pointer font-medium">
        Meal List Debug Info
      </summary>
      <div className="mt-2 space-y-2 text-xs">
        <div>
          <strong>Meals Count:</strong> {meals.items.length}
        </div>
        <div>
          <strong>Loading:</strong> {meals.isLoading.toString()}
        </div>
        <div>
          <strong>Error:</strong> {meals.isError.toString()}
        </div>
        <div>
          <strong>Deleting Map:</strong> {JSON.stringify(meals.isDeletingMap)}
        </div>
        <div>
          <strong>Selected Meal:</strong> {JSON.stringify(nutrition.selectedMeal)}
        </div>
        <div>
          <strong>Nutrition Cache Size:</strong> {nutrition.nutritionCache.size}
        </div>
      </div>
    </details>
  );
}