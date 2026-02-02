'use client';

import { useState } from 'react';
import { Plus, X, BarChart3, ChevronDown, Edit2, Trash2, Eye } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

export interface MealItem {
  id: string;
  name: string;
  meal_type: 'main' | 'snack';
  meal_index: number | null;
  serving_count?: number | null;
  note?: string | null;
  // 栄養情報（オプション）
  calories?: number;
  protein?: number;
  fat?: number;
  carbohydrate?: number;
}

interface CompactMealListProps {
  mealItems: MealItem[];
  mealsPerDay: number;
  onDelete: (itemId: string) => void;
  onEdit?: (mealItem: MealItem) => void;
  onAddClick: (mealType: 'main' | 'snack', mealIndex?: number) => void;
  onAnalyzeNutrition?: (mealType: 'main' | 'snack', mealIndex?: number) => void;
  isDeleting?: boolean;
  // 新しいキャッシュベースの栄養分析props
  getNutritionDataFromCache?: (mealType: 'main' | 'snack', mealIndex?: number) => any;
  onShowNutritionDetails?: (nutritionData: any) => void;
  // 既存UI用に残す（後で削除予定）
  selectedMealForNutrition?: { meal_type: 'main' | 'snack'; meal_index: number | null } | null;
  nutritionData?: {
    meal: any;
    daily: any;
  };
  isNutritionLoading?: boolean;
  nutritionError?: boolean;
  onClearNutritionAnalysis?: () => void;
  onRefetchNutrition?: () => void;
}

export function CompactMealList({
  mealItems,
  mealsPerDay,
  onDelete,
  onEdit,
  onAddClick,
  onAnalyzeNutrition,
  isDeleting = false,
  getNutritionDataFromCache,
  onShowNutritionDetails,
  // 既存UI用に残す
  selectedMealForNutrition,
  nutritionData,
  isNutritionLoading,
  nutritionError,
  onClearNutritionAnalysis,
  onRefetchNutrition,
}: CompactMealListProps) {
  // アコーディオンの開閉状態管理
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  // アイテムの開閉を切り替え
  const toggleExpanded = (itemId: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId);
    } else {
      newExpanded.add(itemId);
    }
    setExpandedItems(newExpanded);
  };

  // 食事を回数別にグループ化
  const groupedMeals = {
    main: Array.from({ length: mealsPerDay }, (_, i) => i + 1).map(index => ({
      index,
      items: mealItems.filter(item => item.meal_type === 'main' && item.meal_index === index),
    })),
    snacks: mealItems.filter(item => item.meal_type === 'snack'),
  };

  // カロリー計算（仮の値、実際はAPIから取得）
  const estimateCalories = (item: MealItem): number => {
    if (item.calories) return item.calories;
    // 簡易推定（実際の実装では栄養データベースから取得）
    const baseCalories = item.name.includes('ご飯') ? 240 :
                        item.name.includes('とんかつ') ? 450 :
                        item.name.includes('パン') ? 200 :
                        item.name.includes('卵') ? 80 :
                        item.name.includes('牛乳') ? 140 : 100;
    return Math.round(baseCalories * (item.serving_count || 1));
  };

  // PFC推定（簡易計算、実際はAPIから取得）
  const estimateNutrients = (item: MealItem) => {
    const calories = estimateCalories(item);

    // 食品別の大まかなPFC比率で推定
    let protein = 0, fat = 0, carbohydrate = 0;

    if (item.name.includes('とんかつ')) {
      protein = calories * 0.20 / 4; // 20%をたんぱく質
      fat = calories * 0.35 / 9;     // 35%を脂質
      carbohydrate = calories * 0.45 / 4; // 45%を炭水化物
    } else if (item.name.includes('ご飯')) {
      protein = calories * 0.08 / 4; // 8%をたんぱく質
      fat = calories * 0.02 / 9;     // 2%を脂質
      carbohydrate = calories * 0.90 / 4; // 90%を炭水化物
    } else if (item.name.includes('卵')) {
      protein = calories * 0.35 / 4; // 35%をたんぱく質
      fat = calories * 0.60 / 9;     // 60%を脂質
      carbohydrate = calories * 0.05 / 4; // 5%を炭水化物
    } else if (item.name.includes('牛乳')) {
      protein = calories * 0.25 / 4; // 25%をたんぱく質
      fat = calories * 0.50 / 9;     // 50%を脂質
      carbohydrate = calories * 0.25 / 4; // 25%を炭水化物
    } else {
      // デフォルト（バランス型）
      protein = calories * 0.20 / 4;
      fat = calories * 0.25 / 9;
      carbohydrate = calories * 0.55 / 4;
    }

    return {
      calories,
      protein: Math.round(protein * 10) / 10,
      fat: Math.round(fat * 10) / 10,
      carbohydrate: Math.round(carbohydrate * 10) / 10,
    };
  };

  // 食事ごとの合計栄養素計算
  const calculateMealTotals = (items: MealItem[]) => {
    return items.reduce((total, item) => {
      const nutrients = estimateNutrients(item);
      return {
        calories: total.calories + nutrients.calories,
        protein: total.protein + nutrients.protein,
        fat: total.fat + nutrients.fat,
        carbohydrate: total.carbohydrate + nutrients.carbohydrate,
      };
    }, { calories: 0, protein: 0, fat: 0, carbohydrate: 0 });
  };

  const MealSection = ({
    title,
    items,
    onAdd,
    onAnalyze,
    mealType,
    mealIndex,
    emptyMessage = "(まだ記録がありません)"
  }: {
    title: string;
    items: MealItem[];
    onAdd: () => void;
    onAnalyze?: () => void;
    mealType: 'main' | 'snack';
    mealIndex?: number;
    emptyMessage?: string;
  }) => {
    const totals = calculateMealTotals(items);

    // データの有無判定: カロリーがあるか、アイテムが存在するかで判定
    const hasData = totals.calories > 0 || items.length > 0;

    // このセクションの栄養データがキャッシュに存在するかチェック
    const cachedNutritionData = getNutritionDataFromCache?.(mealType, mealIndex);
    const hasNutritionData = Boolean(cachedNutritionData);

    return (
    <div className="space-y-2">
      {/* セクションヘッダー */}
      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h3 className="font-medium text-sm">{title}</h3>
            {/* 食事の合計値表示 */}
            {items.length > 0 && (
              <div className="text-xs">
                <span className="text-gray-600 dark:text-gray-400">Total:</span>
                <span className="ml-1 font-bold text-gray-900 dark:text-white">
                  {Math.round(totals.calories)} kcal
                </span>
                <span className="ml-3 text-gray-600 dark:text-gray-400">P:</span>
                <span className="ml-1 font-semibold text-emerald-600 dark:text-emerald-400">
                  {totals.protein.toFixed(1)}g
                </span>
                <span className="ml-3 text-gray-600 dark:text-gray-400">F:</span>
                <span className="ml-1 font-medium text-yellow-600 dark:text-yellow-400">
                  {totals.fat.toFixed(1)}g
                </span>
                <span className="ml-3 text-gray-600 dark:text-gray-400">C:</span>
                <span className="ml-1 font-medium text-blue-600 dark:text-blue-400">
                  {totals.carbohydrate.toFixed(1)}g
                </span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-1">
            {hasData ? (
              /* データがある場合: アイコン化で省スペース */
              <>
                {/* 栄養分析ボタン（アイコンのみ） */}
                {onAnalyze && (
                  <button
                    onClick={onAnalyze}
                    className="p-2 text-gray-400 hover:text-emerald-400 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-full transition-all"
                    title="栄養分析詳細を見る"
                  >
                    <BarChart3 className="w-4 h-4" />
                  </button>
                )}

                {/* 追加ボタン（アイコンのみ） */}
                <button
                  onClick={onAdd}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-full transition-all"
                  title="この食事に食品を追加"
                >
                  <Plus className="w-4 h-4" />
                </button>

                {/* 詳細ボタン（アイコンのみ） */}
                <button
                  onClick={() => hasNutritionData && onShowNutritionDetails?.(cachedNutritionData)}
                  disabled={!hasNutritionData}
                  className={cn(
                    "p-2 rounded-full transition-all",
                    hasNutritionData
                      ? "text-blue-600 hover:text-blue-700 hover:bg-blue-50 dark:hover:bg-blue-900/20"
                      : "text-gray-300 cursor-not-allowed"
                  )}
                  title={hasNutritionData ? "栄養分析詳細を表示" : "栄養分析を実行してください"}
                  aria-label={hasNutritionData ? "栄養分析詳細を表示" : "栄養分析未実行のため無効"}
                >
                  <Eye className="w-4 h-4" />
                </button>
              </>
            ) : (
              /* データがない場合: 追加ボタンを強調 */
              <button
                onClick={onAdd}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-emerald-600 bg-emerald-50 hover:bg-emerald-100 dark:text-emerald-400 dark:bg-emerald-500/10 dark:hover:bg-emerald-500/20 rounded transition-all"
              >
                <Plus className="w-4 h-4" />
                食事を追加
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 区切り線 */}
      <div className="border-t border-dashed border-muted-foreground/30" />

      {/* 食事アイテム */}
      <div className="space-y-0">
        {items.length === 0 ? (
          <div className="text-xs text-muted-foreground py-3 pl-4">
            {emptyMessage}
          </div>
        ) : (
          items.map((item) => {
            const isExpanded = expandedItems.has(item.id);
            const nutrients = estimateNutrients(item);

            return (
              <div
                key={item.id}
                className="border-b border-gray-100 dark:border-gray-800 last:border-0"
              >
                {/* 1. クリック可能なメイン行 */}
                <div
                  onClick={() => toggleExpanded(item.id)}
                  className={`
                    flex justify-between items-center p-3 cursor-pointer group transition-colors duration-200
                    ${isExpanded
                      ? 'bg-gray-50 dark:bg-gray-800/50'
                      : 'hover:bg-gray-50/50 dark:hover:bg-gray-800/30'
                    }
                  `}
                >
                  {/* 左側：食品名・量 */}
                  <div className="flex flex-col gap-1">
                    <span className="text-gray-900 dark:text-gray-100 font-medium group-hover:text-gray-700 dark:group-hover:text-white transition-colors">
                      {item.name}
                    </span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {item.serving_count ? `${item.serving_count}人前` : '1人前'}
                    </span>
                    {item.note && (
                      <span className="text-xs text-gray-400 dark:text-gray-500 italic">
                        {item.note}
                      </span>
                    )}
                  </div>

                  {/* 右側：カロリー・タンパク質(P)・開閉アイコン */}
                  <div className="flex items-center gap-4 text-right">
                    <div className="flex flex-col items-end">
                      <span className="text-sm font-mono font-bold text-gray-900 dark:text-gray-100">
                        {nutrients.calories} <span className="text-xs font-normal text-gray-500 dark:text-gray-400">kcal</span>
                      </span>
                      {/* タンパク質は常時表示 */}
                      <span className="text-xs font-mono text-emerald-600 dark:text-emerald-400">
                        P: {nutrients.protein.toFixed(1)}g
                      </span>
                    </div>

                    {/* 開閉インジケータ */}
                    <ChevronDown
                      className={`w-4 h-4 text-gray-600 dark:text-gray-500 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}
                    />
                  </div>
                </div>

                {/* 2. 詳細エリア（アコーディオン中身） */}
                <div
                  className={`
                    overflow-hidden transition-all duration-300 ease-in-out
                    ${isExpanded ? 'max-h-32 opacity-100' : 'max-h-0 opacity-0'}
                  `}
                >
                  <div className="px-3 pb-3 bg-gray-50 dark:bg-gray-800/50 flex justify-between items-end">

                    {/* 栄養素詳細（バッジ表示） */}
                    <div className="flex gap-2">
                      {/* 脂質 */}
                      <div className="flex flex-col px-3 py-1.5 rounded-md bg-yellow-100 dark:bg-yellow-400/10 border border-yellow-200 dark:border-yellow-400/20">
                        <span className="text-[10px] text-yellow-700 dark:text-yellow-500 uppercase font-bold">Fat</span>
                        <span className="text-sm font-mono text-yellow-800 dark:text-yellow-300">{nutrients.fat.toFixed(1)}g</span>
                      </div>
                      {/* 炭水化物 */}
                      <div className="flex flex-col px-3 py-1.5 rounded-md bg-blue-100 dark:bg-blue-400/10 border border-blue-200 dark:border-blue-400/20">
                        <span className="text-[10px] text-blue-700 dark:text-blue-500 uppercase font-bold">Carbs</span>
                        <span className="text-sm font-mono text-blue-800 dark:text-blue-300">{nutrients.carbohydrate.toFixed(1)}g</span>
                      </div>
                    </div>

                    {/* 操作ボタンエリア */}
                    <div className="flex gap-2">
                      {onEdit && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onEdit(item);
                          }}
                          className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-200 dark:hover:bg-gray-700 rounded-md transition-colors"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                          編集
                        </button>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDelete(item.id);
                        }}
                        disabled={isDeleting}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-400/10 rounded-md transition-colors disabled:opacity-50"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                        削除
                      </button>
                    </div>

                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

    </div>
  );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>今日の食事</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* メイン食事（回数別） */}
        {groupedMeals.main.map(({ index, items }) => (
          <MealSection
            key={index}
            title={`${index}回目の食事`}
            items={items}
            onAdd={() => onAddClick('main', index)}
            onAnalyze={onAnalyzeNutrition ? () => onAnalyzeNutrition('main', index) : undefined}
            mealType="main"
            mealIndex={index}
          />
        ))}

        {/* 間食 */}
        <MealSection
          title="間食"
          items={groupedMeals.snacks}
          onAdd={() => onAddClick('snack')}
          onAnalyze={onAnalyzeNutrition ? () => onAnalyzeNutrition('snack') : undefined}
          mealType="snack"
        />
      </CardContent>
    </Card>
  );
}