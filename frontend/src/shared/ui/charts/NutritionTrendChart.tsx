'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export interface NutritionTrendData {
  date: string; // YYYY-MM-DD
  calories?: number;
  protein?: number;
  carbs?: number;
  fat?: number;
  fiber?: number;
  [nutrient: string]: number | string | undefined;
}

interface NutritionTrendChartProps {
  data: NutritionTrendData[];
  selectedNutrients?: string[];
  onNutrientChange?: (nutrients: string[]) => void;
  className?: string;
}

const NUTRIENT_COLORS = {
  calories: '#ef4444', // red-500
  protein: '#3b82f6', // blue-500
  carbs: '#f59e0b', // amber-500
  fat: '#10b981', // emerald-500
  fiber: '#8b5cf6', // violet-500
  sodium: '#f97316', // orange-500
  sugar: '#ec4899', // pink-500
  calcium: '#06b6d4', // cyan-500
  iron: '#84cc16', // lime-500
  vitaminC: '#6366f1', // indigo-500
} as const;

const NUTRIENT_LABELS = {
  calories: 'カロリー (kcal)',
  protein: 'タンパク質 (g)',
  carbs: '炭水化物 (g)',
  fat: '脂質 (g)',
  fiber: '食物繊維 (g)',
  sodium: 'ナトリウム (mg)',
  sugar: '糖質 (g)',
  calcium: 'カルシウム (mg)',
  iron: '鉄 (mg)',
  vitaminC: 'ビタミンC (mg)',
} as const;

// ツールチップコンポーネントを外部に定義
const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ dataKey: string; value: number; color: string }>; label?: string }) => {
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' });
    } catch {
      return dateString;
    }
  };

  if (active && payload && payload.length) {
    return (
      <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
        <p className="text-sm font-medium mb-2">{formatDate(label || '')}</p>
        {payload.map((entry, index: number) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {NUTRIENT_LABELS[entry.dataKey as keyof typeof NUTRIENT_LABELS] ||
              entry.dataKey}
            : {entry.value?.toFixed(1)}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export function NutritionTrendChart({
  data,
  selectedNutrients = ['calories', 'protein', 'carbs', 'fat'],
  onNutrientChange,
  className,
}: NutritionTrendChartProps) {
  // データが空の場合
  if (!data || data.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>栄養トレンド</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-sm text-muted-foreground">
            データがありません
          </div>
        </CardContent>
      </Card>
    );
  }

  // 利用可能な栄養素を抽出
  const availableNutrients = Object.keys(NUTRIENT_LABELS).filter((nutrient) =>
    data.some((item) => typeof item[nutrient] === 'number')
  );

  // 日付フォーマット関数
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' });
    } catch {
      return dateString;
    }
  };

  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle>栄養トレンド</CardTitle>
        {onNutrientChange && (
          <Select
            value={selectedNutrients.join(',')}
            onValueChange={(value) => {
              onNutrientChange(value.split(',').filter(Boolean));
            }}
          >
            <SelectTrigger className="w-40">
              <SelectValue placeholder="栄養素を選択" />
            </SelectTrigger>
            <SelectContent>
              {availableNutrients.map((nutrient) => (
                <SelectItem key={nutrient} value={nutrient}>
                  {NUTRIENT_LABELS[nutrient as keyof typeof NUTRIENT_LABELS]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="date"
                tickFormatter={formatDate}
                className="text-xs fill-muted-foreground"
                tick={{ fontSize: 12 }}
              />
              <YAxis className="text-xs fill-muted-foreground" tick={{ fontSize: 12 }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ fontSize: '12px' }}
                formatter={(value) =>
                  NUTRIENT_LABELS[value as keyof typeof NUTRIENT_LABELS] || value
                }
              />
              {selectedNutrients.map((nutrient) => (
                <Line
                  key={nutrient}
                  type="monotone"
                  dataKey={nutrient}
                  stroke={NUTRIENT_COLORS[nutrient as keyof typeof NUTRIENT_COLORS] || '#6b7280'}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                  connectNulls={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}