'use client';

import { useRouter } from 'next/navigation';
import type { MealItem } from '@/modules/meal/contract/mealContract';

// Shared UI
import { LoadingState } from '@/shared/ui/Status/LoadingState';
import { ErrorState } from '@/shared/ui/Status/ErrorState';
import { DailySummaryCard } from '@/shared/ui/cards/DailySummaryCard';
import { MealListSection } from '@/shared/ui/sections/MealListSection';
import { NutritionAnalysisCard } from '@/shared/ui/cards/NutritionAnalysisCard';
import { DailyReportCard } from '@/shared/ui/cards/DailyReportCard';
import { EnhancedDailyReportCard } from '@/shared/ui/cards/EnhancedDailyReportCard';
import { NutrientProgressSection } from '@/shared/ui/sections/NutrientProgressSection';

// Feature Modules
import { MealRecommendationCard, MealRecommendationDetailModal, useMealRecommendationModel } from '@/modules/meal-recommendation';
import { useTodayPageModel } from '../model/useTodayPageModel';

// Local Components & Hooks
import { AddMealModal, type AddMealFormValues } from './components/AddMealModal';
import { EditMealModal, type EditMealFormValues } from './components/EditMealModal';
import { useAddMealModalState } from './hooks/useAddMealModalState';
import { useEditMealModalState } from './hooks/useEditMealModalState';
import { useMealRecommendationModalState } from './hooks/useMealRecommendationModalState';
import { useNutritionAnalysisModalState } from './hooks/useNutritionAnalysisModalState';
import { useMealSectionNutritionManager } from './hooks/useMealSectionNutritionManager';
import type { DailySummaryData } from '@/shared/ui/cards/DailySummaryCard';

interface TodayPageContentProps {
  date: string;
}

export function TodayPageContent({ date }: TodayPageContentProps) {
  const router = useRouter();

  // Page Model
  const m = useTodayPageModel({ date });
  const mealRecommendationModel = useMealRecommendationModel({ date });

  // Modal States
  const addMealModal = useAddMealModalState();
  const editMealModal = useEditMealModalState();
  const mealRecommendationModal = useMealRecommendationModalState();
  const nutritionAnalysisModal = useNutritionAnalysisModalState();

  // Nutrition Manager
  const mealSectionNutritionManager = useMealSectionNutritionManager({
    date,
    mealItems: m.meals.mealItems,
  });


  // Meal Handlers
  const handleAddClick = (mealType: 'main' | 'snack', mealIndex?: number) => {
    addMealModal.open(mealType, mealIndex);
  };

  const handleAddModalSubmit = async (values: AddMealFormValues) => {
    await m.meals.createMeal(values);
    addMealModal.close();
  };

  const handleEditClick = (mealItem: MealItem) => {
    editMealModal.open(mealItem, date);
  };

  const handleEditModalSubmit = async (values: EditMealFormValues) => {
    if (editMealModal.editingMealItem) {
      await m.meals.updateMeal(editMealModal.editingMealItem.id, values);
      editMealModal.close();
    }
  };

  // Nutrition Handlers
  const handleNutritionAnalysis = async (mealType: 'main' | 'snack', mealIndex?: number) => {
    try {
      await mealSectionNutritionManager.fetchMealNutrition(mealType, mealIndex);
      m.nutritionAnalysis.selectMealForNutrition(mealType, mealIndex ?? null);
    } catch (error) {
      console.error('Nutrition analysis error:', error);
    }
  };

  const handleShowNutritionDetails = (nutritionData: any) => {
    nutritionAnalysisModal.open(nutritionData);
  };

  // Recommendation Handler
  const handleShowMealRecommendationDetails = () => {
    const currentRecommendation = mealRecommendationModel.recommendation;
    if (currentRecommendation) {
      mealRecommendationModal.open(currentRecommendation);
    }
  };

  // Loading & Error States
  if (m.isLoading) return <LoadingState label="データを読み込み中..." />;
  if (m.isError) {
    return (
      <ErrorState
        title="データの取得に失敗"
        message="BFF/Backend の疎通を確認してください。"
        onRetry={() => router.refresh()}
      />
    );
  }

  // Derived Data
  const profile = m.profile.profile;
  const mealsPerDay = profile?.meals_per_day ?? 3;
  const mealItems = m.meals.mealItems;

  // for DailySummaryCard props
  const dailySummaryData: DailySummaryData | null = m.nutrition.dailySummaryData;
  const isDailySummaryLoading: boolean = m.nutrition.isDailySummaryLoading;

  return (
    <div className="w-full space-y-6">
      <div data-tour="daily-summary">
        <DailySummaryCard
          data={dailySummaryData}
          isLoading={isDailySummaryLoading}
        />
      </div>

      <div data-tour="meal-recommendation">
        <MealRecommendationCard
          date={date}
          onViewDetails={handleShowMealRecommendationDetails}
        />
      </div>

      <div data-tour="meal-list">
        <MealListSection
          mealItems={m.meals.mealItems}
          mealsPerDay={mealsPerDay}
          isLoading={m.meals.isLoading}
          isDeleting={m.meals.isDeleting}
          onAddMeal={handleAddClick}
          onEditMeal={handleEditClick}
          onDeleteMeal={(id: string) => m.meals.deleteMeal(id)}
          onAnalyzeNutrition={handleNutritionAnalysis}
          getNutritionDataFromCache={mealSectionNutritionManager.getMealNutritionFromCache}
          onShowNutritionDetails={handleShowNutritionDetails}
          selectedMealForNutrition={m.nutritionAnalysis.selectedMealForNutrition}
          nutritionData={m.nutritionAnalysis.nutritionData}
          isNutritionLoading={m.nutritionAnalysis.isLoadingNutrition}
          nutritionError={m.nutritionAnalysis.isErrorNutrition}
          onClearNutritionAnalysis={m.nutritionAnalysis.clearSelectedMeal}
          onRefetchNutrition={() => m.nutritionAnalysis.refetchNutrition()}
        />
      </div>

      <div data-tour="target-progress">
        <NutrientProgressSection
          activeTarget={m.nutrition.activeTarget}
          nutrientProgress={m.nutrition.nutrientProgress}
          isLoading={m.nutrition.isDailySummaryLoading}
          isError={m.nutrition.isDailySummaryError}
          onRetry={m.nutrition.refetchDailySummary}
          mealItemsCount={mealItems.length}
        />
      </div>

      <div data-tour="daily-report">
        {m.dailyReport.report ? (
          <EnhancedDailyReportCard
            report={m.dailyReport.report}
            isLoading={m.dailyReport.isLoading}
            onShare={() => console.log('Share report')}
            onExport={() => console.log('Export report')}
          />
        ) : (
          <DailyReportCard
            date={date}
            report={m.dailyReport.report}
            isLoading={m.dailyReport.isLoading}
            isError={m.dailyReport.isError}
            isGenerating={m.dailyReport.isGenerating}
            generateError={m.dailyReport.generateError}
            queryError={m.dailyReport.error}
            isMealCompletionValid={m.mealCompletion.isValid}
            mealCompletionStatus={m.mealCompletion.status}
            missingMealsCount={m.mealCompletion.missingCount}
            hasEnoughData={m.mealCompletion.hasEnoughData}
            onGenerate={(targetDate) => m.dailyReport.generateReport()}
            onFetch={(targetDate) => m.dailyReport.refetch()}
          />
        )}
      </div>

      <AddMealModal
        isOpen={addMealModal.isOpen}
        onClose={addMealModal.close}
        onSubmit={handleAddModalSubmit}
        mealType={addMealModal.selectedMealType}
        mealIndex={addMealModal.selectedMealIndex}
        date={date}
        isLoading={m.meals.createMutation.isPending}
        error={m.meals.createMutation.isError
          ? '追加に失敗しました。/meal-items エンドポイントを確認してください。'
          : null
        }
      />

      <EditMealModal
        isOpen={editMealModal.isOpen}
        onClose={editMealModal.close}
        onSubmit={handleEditModalSubmit}
        mealItem={editMealModal.editingMealItem}
        isLoading={m.meals.updateMutation.isPending}
        error={m.meals.updateMutation.isError
          ? '更新に失敗しました。/meal-items/{id} エンドポイントを確認してください。'
          : null
        }
      />

      {m.meals.deleteMutation.isError && (
        <div className="text-sm text-destructive">
          削除に失敗しました。/meal-items/{'{id}'} を確認してください。
        </div>
      )}

      {nutritionAnalysisModal.isOpen && nutritionAnalysisModal.nutritionDetailsData && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-900 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-auto">
            <NutritionAnalysisCard
              mealData={nutritionAnalysisModal.nutritionDetailsData.meal}
              dailyData={nutritionAnalysisModal.nutritionDetailsData.daily}
              onClose={nutritionAnalysisModal.close}
              isLoading={false}
            />
          </div>
        </div>
      )}

      <MealRecommendationDetailModal
        recommendation={mealRecommendationModal.selectedRecommendation}
        isOpen={mealRecommendationModal.isOpen}
        onClose={mealRecommendationModal.close}
        onShare={() => console.log('Share recommendation')}
        onFavorite={() => console.log('Favorite recommendation')}
        onExport={() => console.log('Export recommendation')}
      />
    </div>
  );
}