'use client';

import { useRouter } from 'next/navigation';

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
import { AddMealModal } from './components/modals/AddMealModal';
import { EditMealModal } from './components/modals/EditMealModal';
import { useAddMealModalState } from './hooks/useAddMealModalState';
import { useEditMealModalState } from './hooks/useEditMealModalState';
import { useMealRecommendationModalState } from './hooks/useMealRecommendationModalState';
import { useNutritionAnalysisModalState } from './hooks/useNutritionAnalysisModalState';


interface TodayPageContentProps {
  date: string;
}

export function TodayPageContent({ date }: TodayPageContentProps) {
  const router = useRouter();

  // Page Model

  const {
    isPageLoading,
    isPageError,
    profileManager,
    nutritionCalculator,
    mealManager,
    dailyReportManager,
    mealCompletionCalculator,
    nutritionAnalysisState,
    mealSectionState,
    nutritionDataAvailability,
  } = useTodayPageModel({ date });

  const mealRecommendationModel = useMealRecommendationModel({ date });

  // Modal States
  const addMealModal = useAddMealModalState();
  const editMealModal = useEditMealModalState();
  const mealRecommendationModal = useMealRecommendationModalState();
  const nutritionAnalysisModal = useNutritionAnalysisModalState();

  // Handlers
  const handleNutritionAnalysis = async (mealType: 'main' | 'snack', mealIndex?: number) => {
    console.log('🎯 handleNutritionAnalysis called:', { mealType, mealIndex });
    try {
      const result = await mealSectionState.fetchNutrition(mealType, mealIndex);
      console.log('✅ Nutrition fetched successfully:', result);
      nutritionAnalysisState.selectMealForNutrition(mealType, mealIndex ?? null);
      console.log('✅ Meal selected for nutrition display');
    } catch (error) {
      console.error('❌ Nutrition analysis error:', error);
    }
  };

  const handleShowNutritionDetails = (mealType: 'main' | 'snack', mealIndex?: number) => {
    const data = mealSectionState.getFromCache(mealType, mealIndex);
    if (data) {
      nutritionAnalysisModal.open(data);
    }
  };

  // Loading & Error States
  if (isPageLoading) return <LoadingState label="データを読み込み中..." />;
  if (isPageError) {
    return (
      <ErrorState
        title="データの取得に失敗"
        message="BFF/Backend の疎通を確認してください。"
        onRetry={() => router.refresh()}
      />
    );
  }

  // Derived Data
  const profile = profileManager.profile;
  const mealsPerDay = profile?.meals_per_day ?? 3;
  const mealItems = mealManager.mealItems;

  return (
    <div className="w-full space-y-6">
      <div data-tour="daily-summary">
        <DailySummaryCard
          data={nutritionCalculator.dailySummaryData}
          isLoading={nutritionCalculator.isDailySummaryLoading}
        />
      </div>

      <div data-tour="meal-recommendation">
        <MealRecommendationCard
          date={date}
          onViewDetails={() => {
            if (mealRecommendationModel.data.recommendation) {
              mealRecommendationModal.open(mealRecommendationModel.data.recommendation);
            }
          }}
        />
      </div>

      <div data-tour="meal-list">
        <MealListSection
          mealItems={mealItems}
          mealsPerDay={mealsPerDay}
          isLoading={mealManager.isLoading}
          isDeleting={mealManager.isDeleting}
          onAddMeal={addMealModal.open}
          onEditMeal={(mealItem) => editMealModal.open(mealItem, date)}
          onDeleteMeal={mealManager.deleteMeal}
          onAnalyzeNutrition={handleNutritionAnalysis}
          nutritionAnalysis={{
            selectedMeal: nutritionAnalysisState.selectedMealForNutrition,
            data: nutritionAnalysisState.nutritionData,
            isLoading: nutritionAnalysisState.isLoadingNutrition,
            nutritionDataAvailability: nutritionDataAvailability,
            onShowDetails: handleShowNutritionDetails,
            onClear: nutritionAnalysisState.clearSelectedMeal,
          }}
        />
      </div>

      <div data-tour="target-progress">
        <NutrientProgressSection
          nutrientProgress={nutritionCalculator.nutrientProgress}
          progressState={nutritionCalculator.progressState}
          onRetry={nutritionCalculator.refetchDailySummary}
        />
      </div>

      <div data-tour="daily-report">
        {dailyReportManager.report ? (
          <EnhancedDailyReportCard
            report={dailyReportManager.report}
            isLoading={dailyReportManager.isLoading}
            onShare={() => console.log('Share report')}
            onExport={() => console.log('Export report')}
          />
        ) : (
          <DailyReportCard
            date={date}
            dailyReport={{
              report: dailyReportManager.report,
              isLoading: dailyReportManager.isLoading,
              isError: dailyReportManager.isError,
              isGenerating: dailyReportManager.isGenerating,
              generateError: dailyReportManager.generateError,
              onGenerate: dailyReportManager.generateReport,
              onFetch: dailyReportManager.refetch,
            }}
            mealCompletion={{
              isValid: mealCompletionCalculator.isValid,
              status: mealCompletionCalculator.status,
              missingCount: mealCompletionCalculator.missingCount,
              hasEnoughData: mealCompletionCalculator.hasEnoughData,
            }}
          />
        )}
      </div>

      <AddMealModal
        isOpen={addMealModal.isOpen}
        onClose={addMealModal.close}
        onSubmit={async (values) => {
          await mealManager.createMeal(values);
          addMealModal.close();
        }}
        mealType={addMealModal.selectedMealType}
        mealIndex={addMealModal.selectedMealIndex}
        date={date}
        isLoading={mealManager.createMutation.isPending}
        error={mealManager.createMutation.isError
          ? '追加に失敗しました。/meal-items エンドポイントを確認してください。'
          : null
        }
      />

      <EditMealModal
        isOpen={editMealModal.isOpen}
        onClose={editMealModal.close}
        onSubmit={async (values) => {
          if (editMealModal.editingMealItem) {
            await mealManager.updateMeal(editMealModal.editingMealItem.id, values);
            editMealModal.close();
          }
        }}
        mealItem={editMealModal.editingMealItem}
        isLoading={mealManager.updateMutation.isPending}
        error={mealManager.updateMutation.isError
          ? '更新に失敗しました。/meal-items/{id} エンドポイントを確認してください。'
          : null
        }
      />

      {mealManager.deleteMutation.isError && (
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