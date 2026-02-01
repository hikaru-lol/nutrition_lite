'use client';

import { useMemo } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { useRouter } from 'next/navigation';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Settings } from 'lucide-react';

export interface DailySummaryData {
  // カロリー情報
  currentCalories: number;
  targetCalories: number;

  // PFCバランス (grams)
  protein: {
    current: number;
    target: number;
  };
  fat: {
    current: number;
    target: number;
  };
  carbohydrate: {
    current: number;
    target: number;
  };
}

interface DailySummaryCardProps {
  data: DailySummaryData | null;
  isLoading?: boolean;
}

const PFC_COLORS = {
  protein: '#22c55e', // 緑
  fat: '#eab308',     // 黄
  carbohydrate: '#3b82f6', // 青
};

export function DailySummaryCard({ data, isLoading }: DailySummaryCardProps) {
  const router = useRouter();

  // PFCバランス用のデータ準備
  const pfcData = useMemo(() => {
    if (!data) return [];

    const totalPFC = data.protein.current + data.fat.current + data.carbohydrate.current;
    if (totalPFC === 0) return [];

    return [
      {
        name: 'タンパク質',
        value: data.protein.current,
        percentage: (data.protein.current / totalPFC) * 100,
        color: PFC_COLORS.protein,
        target: data.protein.target,
        achievement: data.protein.target > 0 ? (data.protein.current / data.protein.target) * 100 : 0,
      },
      {
        name: '脂質',
        value: data.fat.current,
        percentage: (data.fat.current / totalPFC) * 100,
        color: PFC_COLORS.fat,
        target: data.fat.target,
        achievement: data.fat.target > 0 ? (data.fat.current / data.fat.target) * 100 : 0,
      },
      {
        name: '炭水化物',
        value: data.carbohydrate.current,
        percentage: (data.carbohydrate.current / totalPFC) * 100,
        color: PFC_COLORS.carbohydrate,
        target: data.carbohydrate.target,
        achievement: data.carbohydrate.target > 0 ? (data.carbohydrate.current / data.carbohydrate.target) * 100 : 0,
      },
    ];
  }, [data]);

  // カロリー達成率
  const caloriePercentage = useMemo(() => {
    if (!data || data.targetCalories === 0) return 0;
    return (data.currentCalories / data.targetCalories) * 100;
  }, [data]);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>本日のサマリー</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse">
            <div className="h-16 bg-muted rounded mb-4"></div>
            <div className="h-32 bg-muted rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>本日のサマリー</CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={() => router.push('/targets')}
            className="gap-2"
          >
            <Settings className="h-4 w-4" />
            目標設定
          </Button>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            目標を設定すると栄養サマリーが表示されます
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>本日のサマリー</CardTitle>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/targets')}
          className="gap-2 text-muted-foreground hover:text-foreground"
        >
          <Settings className="h-4 w-4" />
          目標設定
        </Button>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* カロリー表示 */}
        <div className="text-center space-y-2">
          <div className="text-3xl font-bold">
            {data.currentCalories.toLocaleString()} / {data.targetCalories.toLocaleString()}
            <span className="text-lg text-muted-foreground ml-2">kcal</span>
          </div>
          <div className="text-sm text-muted-foreground">
            摂取カロリー達成率: {caloriePercentage.toFixed(0)}%
          </div>

          {/* カロリー進捗バー */}
          <div className="w-full bg-muted rounded-full h-2">
            <div
              className="h-2 rounded-full transition-all duration-300"
              style={{
                width: `${Math.min(caloriePercentage, 100)}%`,
                backgroundColor: caloriePercentage < 80 ? '#eab308' :
                                caloriePercentage <= 100 ? '#22c55e' : '#ef4444'
              }}
            />
          </div>
        </div>

        {/* PFCバランス */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* PFC円グラフ */}
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-center">PFCバランス</h3>
            {pfcData.length > 0 ? (
              <div className="h-32">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pfcData}
                      cx="50%"
                      cy="50%"
                      innerRadius={20}
                      outerRadius={50}
                      dataKey="value"
                    >
                      {pfcData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-32 flex items-center justify-center text-muted-foreground text-xs">
                データなし
              </div>
            )}
          </div>

          {/* PFC詳細 */}
          <div className="space-y-2">
            <h3 className="text-sm font-medium">PFC達成度</h3>
            <div className="space-y-2">
              {pfcData.map((item) => (
                <div key={item.name} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: item.color }}
                      />
                      <span>{item.name}</span>
                    </div>
                    <span className="font-medium">
                      {item.value.toFixed(1)}g / {item.target.toFixed(1)}g
                    </span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-1">
                    <div
                      className="h-1 rounded-full transition-all duration-300"
                      style={{
                        width: `${Math.min(item.achievement, 100)}%`,
                        backgroundColor: item.color,
                        opacity: item.achievement < 80 ? 0.6 : 1,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}