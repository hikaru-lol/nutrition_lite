'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { X } from 'lucide-react';

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

const nutrientLabels: Record<string, string> = {
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
  vitamin_a: 'ビタミンA',
  vitamin_b_complex: 'ビタミンB群',
  vitamin_c: 'ビタミンC',
  vitamin_e: 'ビタミンE',
  vitamin_k: 'ビタミンK',
  magnesium: 'マグネシウム',
  zinc: '亜鉛',
};

export function NutritionAnalysisCard({
  mealData,
  dailyData,
  onClose,
  isLoading = false,
}: NutritionAnalysisCardProps) {
  const mealTypeLabel = mealData.meal_type === 'main' ? 'メイン' : '間食';
  const mealTitle = mealData.meal_type === 'main' && mealData.meal_index
    ? `${mealTypeLabel} ${mealData.meal_index}`
    : mealTypeLabel;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-base font-medium">
          栄養分析 - {mealTitle} ({mealData.date})
        </CardTitle>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          className="h-8 w-8 p-0"
        >
          <X className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-sm text-muted-foreground">計算中...</div>
        ) : (
          <div className="space-y-6">
            {/* 食事別の栄養素 */}
            <div>
              <h4 className="text-sm font-medium mb-3">この食事の栄養素</h4>
              <div className="space-y-2">
                {mealData.nutrients.map((nutrient) => (
                  <div key={nutrient.code} className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">
                      {nutrientLabels[nutrient.code] || nutrient.code}
                    </span>
                    <span className="font-medium">
                      {nutrient.value.toFixed(1)} {nutrient.unit}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* 1日分の栄養素サマリー */}
            <div>
              <h4 className="text-sm font-medium mb-3">本日の栄養素合計</h4>
              <div className="space-y-3">
                {dailyData.nutrients.map((nutrient) => {
                  const mealNutrient = mealData.nutrients.find(n => n.code === nutrient.code);
                  const percentage = mealNutrient
                    ? (mealNutrient.value / nutrient.value) * 100
                    : 0;

                  return (
                    <div key={nutrient.code} className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">
                          {nutrientLabels[nutrient.code] || nutrient.code}
                        </span>
                        <span className="font-medium">
                          {nutrient.value.toFixed(1)} {nutrient.unit}
                        </span>
                      </div>
                      {mealNutrient && (
                        <div className="flex items-center gap-2">
                          <Progress value={Math.min(percentage, 100)} className="flex-1 h-2" />
                          <span className="text-xs text-muted-foreground w-12">
                            {percentage.toFixed(0)}%
                          </span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* メタデータ */}
            <div className="pt-2 border-t text-xs text-muted-foreground">
              <div>食事分析: {new Date(mealData.generated_at).toLocaleString()}</div>
              <div>1日分析: {new Date(dailyData.generated_at).toLocaleString()}</div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}