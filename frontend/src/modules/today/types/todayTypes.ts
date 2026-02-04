/**
 * TodayPageリファクタリング用の型定義
 *
 * 既存のuseTodayPageModelから抽出した型とドメイン別の新しい型定義
 */

import { z } from 'zod';
import type { MealItemResponse } from '@/modules/meal/contract/mealContract';
import type { Target } from '@/modules/target/contract/targetContract';
import type { Profile } from '@/modules/profile/contract/profileContract';
import type { NutrientCode } from '@/modules/target/contract/targetContract';
import type {
  DailyNutritionSummary,
  DailyNutritionReport,
} from '@/modules/nutrition/contract/nutritionContract';
import {
  MealItemRequestSchema,
  type MealItemRequest,
  type MealType,
} from '@/modules/meal/contract/mealContract';

// ========================================
// Form関連の型定義
// ========================================

export const TodayMealItemFormSchema = MealItemRequestSchema.extend({
  meal_index: z.number().int().min(1).nullable().optional(),
});

export type TodayMealItemFormValues = z.infer<typeof TodayMealItemFormSchema>;

// ========================================
// 栄養進捗関連の型定義
// ========================================

export type NutrientProgress = {
  code: NutrientCode;
  label: string;
  target: number;
  actual: number;
  unit: string;
  percentage: number;
};

// 栄養素コード → 日本語ラベル
export const nutrientLabels: Record<NutrientCode, string> = {
  carbohydrate: '炭水化物',
  fat: '脂質',
  protein: 'たんぱく質',
  water: '水分',
  fiber: '食物繊維',
  sodium: 'ナトリウム',
  iron: '鉄',
  calcium: 'カルシウム',
  vitamin_d: 'ビタミンD',
  potassium: 'カリウム',
};

// ========================================
// ドメイン別モデル型定義
// ========================================

// 1. 食事管理ドメイン
export interface TodayMealsState {
  items: MealItemResponse[];
  isLoading: boolean;
  isError: boolean;
  isDeletingMap: Record<string, boolean>; // 複数アイテムの削除状態管理
}

export interface TodayMealsActions {
  add: (values: TodayMealItemFormValues) => Promise<void>;
  remove: (id: string) => Promise<void>;
  update: (entryId: string, values: any) => Promise<void>;
}

export interface TodayMealsModel extends TodayMealsState, TodayMealsActions {}

// 2. 目標管理ドメイン
export interface TodayTargetsState {
  activeTarget: Target | null;
  nutrientProgress: NutrientProgress[];
  dailySummaryData: DailyNutritionSummary | null;
  isLoading: boolean;
  isError: boolean;
  isDailySummaryLoading: boolean;
  isDailySummaryError: boolean;
}

export interface TodayTargetsActions {
  refetchDailySummary: () => void;
}

export interface TodayTargetsModel extends TodayTargetsState, TodayTargetsActions {}

// 3. 栄養分析ドメイン
export interface SelectedMeal {
  meal_type: MealType;
  meal_index: number | null;
}

export interface TodayNutritionState {
  selectedMeal: SelectedMeal | null;
  nutritionData: any | null;
  isLoading: boolean;
  isError: boolean;
  nutritionCache: Map<string, any>; // キャッシュ管理
}

export interface TodayNutritionActions {
  selectMeal: (meal_type: MealType, meal_index: number | null) => void;
  clearSelected: () => void;
  analyze: (meal_type: MealType, meal_index?: number) => Promise<any>;
  getFromCache: (meal_type: string, meal_index?: number) => any;
  refetch: () => void;
  showDetails: (data: any) => void;
}

export interface TodayNutritionModel extends TodayNutritionState, TodayNutritionActions {}

// 4. レポート管理ドメイン
export interface TodayReportsState {
  dailyReport: DailyNutritionReport | null;
  enhancedReport: any | null; // EnhancedDailyReportCard用
  isLoading: boolean;
  isError: boolean;
  isGenerating: boolean;
  generateError: any;
  queryError: any;
}

export interface TodayReportsActions {
  generateReport: (date: string) => Promise<void>;
  fetchReport: (date: string) => void;
}

export interface ValidationState {
  isMealCompletionValid: boolean;
  mealCompletionStatus: any;
  missingMealsCount: number;
  hasEnoughData: boolean;
}

export interface TodayReportsModel extends TodayReportsState, TodayReportsActions {
  validationState: ValidationState;
}

// 5. プロフィール管理ドメイン（TodayPageで使用する部分のみ）
export interface TodayProfileState {
  profile: Profile | null;
  mealsPerDay: number;
  isLoading: boolean;
  isError: boolean;
}

export interface TodayProfileModel extends TodayProfileState {}

// 6. モーダル管理ドメイン
export interface AddModalState {
  isOpen: boolean;
  selectedMealType: 'main' | 'snack';
  selectedMealIndex: number;
}

export interface EditModalState {
  isOpen: boolean;
  editingMealItem: any | null; // MealItemForEdit型
}

export interface NutritionModalState {
  isOpen: boolean;
  data: any | null;
}

export interface RecommendationModalState {
  isOpen: boolean;
  recommendation: any | null;
}

export interface TodayModalsState {
  addModal: AddModalState;
  editModal: EditModalState;
  nutritionModal: NutritionModalState;
  recommendationModal: RecommendationModalState;
}

export interface TodayModalsActions {
  openAddModal: (mealType: 'main' | 'snack', mealIndex?: number) => void;
  closeAddModal: () => void;
  openEditModal: (mealItem: MealItemResponse) => void;
  closeEditModal: () => void;
  openNutritionModal: (data: any) => void;
  closeNutritionModal: () => void;
  openRecommendationModal: () => void;
  closeRecommendationModal: () => void;
}

export interface TodayModalsModel extends TodayModalsState, TodayModalsActions {
  // Utility functions
  closeAllModals: () => void;
  hasOpenModal: () => boolean;
}

// ========================================
// Context統合型定義
// ========================================

export interface TodayPageContextValue {
  // メタデータ
  date: string;

  // ドメインモデル
  meals: TodayMealsModel;
  targets: TodayTargetsModel;
  nutrition: TodayNutritionModel;
  reports: TodayReportsModel;
  profile: TodayProfileModel;
  modals: TodayModalsModel;

  // 統合状態
  isLoading: boolean;
  hasError: boolean;
}

// ========================================
// ユーティリティ型
// ========================================

/**
 * 日付フォーマット用
 */
export function formatLocalDateYYYYMMDD(d: Date): string {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

// ========================================
// Migration Types
// ========================================

export interface MigrationFlags {
  useDailySummarySection: boolean;
  useMealListSection: boolean;
  useTargetProgressSection: boolean;
  useDailyReportSection: boolean;
  useModalsContainer: boolean;
  useFullNewLayout: boolean;
}