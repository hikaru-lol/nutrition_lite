'use client';

import { useToday } from '../hooks/useToday';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card';
import { PieChart, Pie, Cell, ResponsiveContainer, Label } from 'recharts';
import { Loader2 } from 'lucide-react';

// 進捗バーの簡易コンポーネント (shadcnのProgressを使っても良いですが、色指定しやすいため自作)
const ProgressBar = ({
  label,
  current,
  target,
  colorClass,
}: {
  label: string;
  current: number;
  target: number;
  colorClass: string;
}) => {
  // 100%を超えても破綻しないようにcapする
  const percentage = Math.min((current / target) * 100, 100);

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs font-medium">
        <span>{label}</span>
        <span className="text-gray-500">
          {Math.round(current)} / {target} g
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
        <div
          className={`h-full ${colorClass}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export const NutritionSummary = () => {
  const { data: summary, isLoading, error } = useToday();

  if (isLoading) {
    return (
      <Card className="flex h-64 w-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </Card>
    );
  }

  if (error || !summary) {
    return (
      <Card className="p-6 text-center text-red-500">
        データの取得に失敗しました
      </Card>
    );
  }

  // カロリー計算
  const remainingCalories = summary.target_calories - summary.total_calories;
  const isOver = remainingCalories < 0;

  // 円グラフ用データ
  const chartData = [
    { name: '摂取', value: summary.total_calories },
    {
      name: '残り',
      value: Math.max(remainingCalories, 0), // マイナスにならないように
    },
  ];
  // 色: 摂取済み=メインカラー, 残り=グレー
  const COLORS = ['#2563eb', '#e5e7eb']; // blue-600, gray-200

  // カロリーオーバー時は赤くする
  if (isOver) {
    COLORS[0] = '#ef4444'; // red-500
  }

  return (
    <Card className="w-full shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg text-gray-700">今日のサマリー</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-6 sm:flex-row sm:items-center">
          {/* 左側: カロリー円グラフ */}
          <div className="relative flex h-40 w-full flex-1 items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={70}
                  startAngle={90}
                  endAngle={-270}
                  dataKey="value"
                  stroke="none"
                >
                  {chartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                  {/* 中央のテキスト表示 */}
                  <Label
                    value={
                      isOver
                        ? `+${Math.abs(Math.round(remainingCalories))}`
                        : `${Math.round(remainingCalories)}`
                    }
                    position="center"
                    className="fill-gray-900 text-xl font-bold"
                  />
                  <Label
                    value={isOver ? 'kcal オーバー' : 'kcal 残り'}
                    position="center"
                    dy={20}
                    className="fill-gray-500 text-xs"
                  />
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* 右側: PFCバランス */}
          <div className="flex-1 space-y-4">
            <ProgressBar
              label="Protein (タンパク質)"
              current={summary.total_protein}
              target={summary.target_protein}
              colorClass="bg-red-500"
            />
            <ProgressBar
              label="Fat (脂質)"
              current={summary.total_fat}
              target={summary.target_fat}
              colorClass="bg-yellow-500"
            />
            <ProgressBar
              label="Carb (炭水化物)"
              current={summary.total_carbs}
              target={summary.target_carbs}
              colorClass="bg-green-500"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
