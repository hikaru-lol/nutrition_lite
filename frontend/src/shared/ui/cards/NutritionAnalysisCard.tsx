'use client';

import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { X, ChevronDown, ChevronUp, Activity, Leaf, Droplet, Anchor, Bone } from 'lucide-react';

import type {
  MealNutritionSummary,
  DailyNutritionSummary,
} from '@/modules/nutrition/contract/nutritionContract';

interface NutritionAnalysisCardProps {
  mealData: MealNutritionSummary;
  dailyData: DailyNutritionSummary;
  onClose: () => void;
  isLoading?: boolean;
}

// 栄養素設定（Config）の定義
type NutrientType = 'pfc' | 'vitamin' | 'mineral' | 'fiber';

interface NutrientConfig {
  label: string;
  type: NutrientType;
  textColor: string;
  bgColor: string;
  darkModeColors: {
    bg: string;
    border: string;
    text: string;
    accent: string;
  };
  icon?: React.ComponentType<{ className?: string }>;
  order: number;
}

const nutrientConfig: Record<string, NutrientConfig> = {
  // 主要栄養素（PFC）
  protein: {
    label: 'たんぱく質',
    type: 'pfc',
    textColor: 'text-red-700',
    bgColor: 'bg-red-50',
    darkModeColors: {
      bg: 'bg-red-500/10',
      border: 'border-red-500/20',
      text: 'text-red-400',
      accent: 'text-red-400/80'
    },
    order: 1
  },
  fat: {
    label: '脂質',
    type: 'pfc',
    textColor: 'text-yellow-700',
    bgColor: 'bg-yellow-50',
    darkModeColors: {
      bg: 'bg-yellow-500/10',
      border: 'border-yellow-500/20',
      text: 'text-yellow-400',
      accent: 'text-yellow-400/80'
    },
    order: 2
  },
  carbohydrate: {
    label: '炭水化物',
    type: 'pfc',
    textColor: 'text-blue-700',
    bgColor: 'bg-blue-50',
    darkModeColors: {
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/20',
      text: 'text-blue-400',
      accent: 'text-blue-400/80'
    },
    order: 3
  },

  // 食物繊維
  fiber: {
    label: '食物繊維',
    type: 'fiber',
    textColor: 'text-green-700',
    bgColor: 'bg-green-50',
    darkModeColors: {
      bg: 'bg-green-500/10',
      border: 'border-green-500/20',
      text: 'text-green-400',
      accent: 'text-green-400/80'
    },
    icon: Leaf,
    order: 4
  },

  // ミネラル
  sodium: {
    label: 'ナトリウム',
    type: 'mineral',
    textColor: 'text-purple-700',
    bgColor: 'bg-purple-50',
    darkModeColors: {
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/20',
      text: 'text-purple-400',
      accent: 'text-purple-400/80'
    },
    icon: Droplet,
    order: 5
  },
  iron: {
    label: '鉄',
    type: 'mineral',
    textColor: 'text-gray-700',
    bgColor: 'bg-gray-50',
    darkModeColors: {
      bg: 'bg-gray-500/10',
      border: 'border-gray-500/20',
      text: 'text-gray-400',
      accent: 'text-gray-400/80'
    },
    icon: Anchor,
    order: 6
  },
  calcium: {
    label: 'カルシウム',
    type: 'mineral',
    textColor: 'text-indigo-700',
    bgColor: 'bg-indigo-50',
    darkModeColors: {
      bg: 'bg-indigo-500/10',
      border: 'border-indigo-500/20',
      text: 'text-indigo-400',
      accent: 'text-indigo-400/80'
    },
    icon: Bone,
    order: 7
  },
  potassium: {
    label: 'カリウム',
    type: 'mineral',
    textColor: 'text-orange-700',
    bgColor: 'bg-orange-50',
    darkModeColors: {
      bg: 'bg-orange-500/10',
      border: 'border-orange-500/20',
      text: 'text-orange-400',
      accent: 'text-orange-400/80'
    },
    order: 8
  },

  // ビタミン
  vitamin_c: {
    label: 'ビタミンC',
    type: 'vitamin',
    textColor: 'text-pink-700',
    bgColor: 'bg-pink-50',
    darkModeColors: {
      bg: 'bg-pink-500/10',
      border: 'border-pink-500/20',
      text: 'text-pink-400',
      accent: 'text-pink-400/80'
    },
    order: 9
  },
  vitamin_d: {
    label: 'ビタミンD',
    type: 'vitamin',
    textColor: 'text-teal-700',
    bgColor: 'bg-teal-50',
    darkModeColors: {
      bg: 'bg-teal-500/10',
      border: 'border-teal-500/20',
      text: 'text-teal-400',
      accent: 'text-teal-400/80'
    },
    order: 10
  }
};

// PFC（主要栄養素）の順序
const pfcNutrients = ['protein', 'fat', 'carbohydrate'];

// その他栄養素（重要度順）
const otherNutrients = Object.entries(nutrientConfig)
  .filter(([code]) => !pfcNutrients.includes(code))
  .sort(([, a], [, b]) => a.order - b.order)
  .map(([code]) => code);

// 安全なデータ取得関数
function findNutrient(nutrients: Array<{code: string, value: number, unit: string}>, code: string) {
  return nutrients.find(n => n.code === code);
}

function getNutrientValue(nutrients: Array<{code: string, value: number, unit: string}>, code: string): number {
  const nutrient = findNutrient(nutrients, code);
  return nutrient?.value ?? 0;
}

function getNutrientUnit(nutrients: Array<{code: string, value: number, unit: string}>, code: string): string {
  const nutrient = findNutrient(nutrients, code);
  return nutrient?.unit ?? 'g';
}

export function NutritionAnalysisCard({
  mealData,
  dailyData,
  onClose,
  isLoading = false,
}: NutritionAnalysisCardProps) {
  const [showAllNutrients, setShowAllNutrients] = useState(false);

  // 食事タイプとタイトルの決定
  const mealTypeLabel = mealData.meal_type === 'main' ? 'メイン' : '間食';
  const mealTitle = mealData.meal_type === 'main' && mealData.meal_index
    ? `${mealTypeLabel} ${mealData.meal_index}`
    : mealTypeLabel;

  // 表示用データの振り分けロジック（useMemo）
  const { pfcData, otherNutrientsData, filteredOtherNutrients } = useMemo(() => {
    // PFC（主要栄養素）データの準備
    const pfcData = pfcNutrients.map(code => {
      const mealNutrient = findNutrient(mealData.nutrients, code);
      const dailyNutrient = findNutrient(dailyData.nutrients, code);
      const config = nutrientConfig[code];

      if (!mealNutrient || !dailyNutrient || !config) return null;

      return {
        code,
        config,
        meal: mealNutrient,
        daily: dailyNutrient,
        percentage: dailyNutrient.value > 0 ? (mealNutrient.value / dailyNutrient.value) * 100 : 0
      };
    }).filter(Boolean);

    // その他栄養素データの準備
    const otherNutrientsData = otherNutrients.map(code => {
      const mealNutrient = findNutrient(mealData.nutrients, code);
      const dailyNutrient = findNutrient(dailyData.nutrients, code);
      const config = nutrientConfig[code];

      if (!mealNutrient || !dailyNutrient || !config) return null;

      return {
        code,
        config,
        meal: mealNutrient,
        daily: dailyNutrient,
        percentage: dailyNutrient.value > 0 ? (mealNutrient.value / dailyNutrient.value) * 100 : 0
      };
    }).filter(Boolean);

    // 簡易表示/詳細表示のフィルタリング
    const filteredOtherNutrients = showAllNutrients
      ? otherNutrientsData
      : otherNutrientsData.slice(0, 4); // 簡易表示では4つまで

    return { pfcData, otherNutrientsData, filteredOtherNutrients };
  }, [mealData.nutrients, dailyData.nutrients, showAllNutrients]);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-emerald-600" />
            <CardTitle className="text-lg font-semibold">栄養分析</CardTitle>
          </div>
          <Badge
            variant={mealData.meal_type === 'main' ? 'default' : 'secondary'}
            className="text-xs"
          >
            {mealTitle}
          </Badge>
          <span className="text-sm text-muted-foreground">
            {mealData.date}
          </span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          className="h-8 w-8 p-0 hover:bg-red-50 hover:text-red-600"
        >
          <X className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-pulse text-sm text-muted-foreground">計算中...</div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* PFCヒーローセクション（Gridレイアウト） */}
            <div>
              <h4 className="text-sm font-medium mb-4">主要栄養素（PFC）</h4>
              <div className="grid grid-cols-3 gap-4">
                {pfcData.map((item) => (
                  <div
                    key={item!.code}
                    className="relative rounded-lg border border-gray-200 bg-gray-50/30 p-4 transition-all hover:shadow-sm
                             dark:border-gray-700/50 dark:bg-gray-800/20 hover:dark:shadow-lg"
                  >
                    {/* 左端アクセントバー */}
                    <div
                      className={`absolute left-0 top-0 bottom-0 w-1 rounded-l-lg
                        ${item!.config.textColor.replace('text-', 'bg-')}
                        dark:${item!.config.darkModeColors.text.replace('text-', 'bg-')}
                      `}
                    />

                    {/* ラベル */}
                    <div className={`text-xs font-bold mb-2 pl-2
                      ${item!.config.textColor}
                      dark:${item!.config.darkModeColors.text}
                    `}>
                      {item!.config.label}
                    </div>

                    {/* 値と単位 */}
                    <div className="flex items-baseline gap-1 mb-2 pl-2">
                      <span className="text-2xl font-bold font-mono text-foreground">
                        {item!.meal.value.toFixed(1)}
                      </span>
                      <span className={`text-sm font-medium
                        ${item!.config.textColor}
                        dark:${item!.config.darkModeColors.accent}
                      `}>
                        {item!.meal.unit}
                      </span>
                    </div>

                    {/* パーセンテージ */}
                    <div className="text-xs text-muted-foreground pl-2">
                      本日の{' '}
                      <span className="text-foreground font-medium font-mono">
                        {item!.percentage.toFixed(0)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 詳細リストと貢献度バー */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-sm font-medium">その他の栄養素</h4>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowAllNutrients(!showAllNutrients)}
                  className="h-6 px-2 text-xs"
                >
                  {showAllNutrients ? (
                    <>
                      <ChevronUp className="h-3 w-3 mr-1" />
                      簡易表示
                    </>
                  ) : (
                    <>
                      <ChevronDown className="h-3 w-3 mr-1" />
                      詳細表示
                    </>
                  )}
                </Button>
              </div>

              <div className="space-y-2">
                {filteredOtherNutrients.map((item) => (
                  <div key={item!.code} className="space-y-1.5 py-1">
                    {/* 上段：アイコン・ラベルと数値 */}
                    <div className="flex items-end justify-between text-sm">
                      <div className="flex items-center gap-2 text-foreground font-medium">
                        {item!.config.icon ? (
                          React.createElement(item!.config.icon, {
                            className: `w-4 h-4 ${item!.config.textColor} dark:${item!.config.darkModeColors.text}`
                          })
                        ) : (
                          <div className={`w-3 h-3 rounded-full ${item!.config.bgColor} ${item!.config.textColor.replace('text-', 'bg-')}`} />
                        )}
                        <span>{item!.config.label}</span>
                      </div>

                      <div className="flex items-baseline gap-1.5">
                        {/* 今回の摂取量 (太字・等幅) */}
                        <span className="font-bold font-mono text-base">
                          {item!.meal.value.toFixed(1)}
                        </span>
                        <span className="text-xs text-muted-foreground mr-1">
                          {item!.meal.unit}
                        </span>

                        {/* 1日合計に対する割合 */}
                        <span className="text-xs text-muted-foreground font-mono">
                          / {item!.daily.value.toFixed(0)} ({item!.percentage.toFixed(0)}%)
                        </span>
                      </div>
                    </div>

                    {/* 下段：スリムなプログレスバー */}
                    <div className="relative h-1.5 w-full bg-secondary rounded-full overflow-hidden">
                      <div
                        className={`absolute top-0 left-0 h-full rounded-full transition-all duration-300 ${
                          item!.percentage > 100 ? 'bg-red-500' :
                          item!.percentage >= 80 ? 'bg-green-500' :
                          'bg-blue-500'
                        }`}
                        style={{ width: `${Math.min(item!.percentage, 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* メタデータ */}
            <div className="pt-4 border-t text-center">
              <div className="text-xs text-muted-foreground">
                {new Date(mealData.generated_at).toLocaleDateString()}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}