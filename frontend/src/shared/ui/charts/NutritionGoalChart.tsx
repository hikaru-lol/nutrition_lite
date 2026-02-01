'use client';

import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
  LabelList,
} from 'recharts';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export interface NutritionGoalData {
  nutrient: string;
  label: string;
  current: number;
  target: number;
  unit: string;
  percentage: number;
}

interface NutritionGoalChartProps {
  data: NutritionGoalData[];
  chartType?: 'pie' | 'bar';
  onChartTypeChange?: (type: 'pie' | 'bar') => void;
  className?: string;
}

const COLORS = {
  achieved: '#10b981', // emerald-500 - 目標達成
  warning: '#f59e0b', // amber-500 - 注意（80-100%）
  danger: '#ef4444', // red-500 - 不足（<80%）
  over: '#8b5cf6', // violet-500 - 超過（>100%）
};

const getColorByPercentage = (percentage: number) => {
  if (percentage > 100) return COLORS.over;
  if (percentage >= 80) return COLORS.achieved;
  if (percentage >= 50) return COLORS.warning;
  return COLORS.danger;
};

// ツールチップコンポーネントを外部に定義
const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: NutritionGoalData }> }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
        <p className="text-sm font-medium mb-1">{data.label}</p>
        <p className="text-sm">
          現在: {data.current.toFixed(1)} {data.unit}
        </p>
        <p className="text-sm">
          目標: {data.target.toFixed(1)} {data.unit}
        </p>
        <p className="text-sm font-medium" style={{ color: getColorByPercentage(data.percentage) }}>
          達成率: {data.percentage.toFixed(1)}%
        </p>
      </div>
    );
  }
  return null;
};

// 円グラフコンポーネントを外部に定義
const PieChartComponent = ({ data }: { data: NutritionGoalData[] }) => {
  const pieData = data.map(item => ({
    name: item.label,
    value: Math.min(item.percentage, 100), // 100%でキャップ
    fullData: item,
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={pieData}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {pieData.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={getColorByPercentage(entry.fullData.percentage)}
            />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
      </PieChart>
    </ResponsiveContainer>
  );
};

// 横棒グラフコンポーネント（達成率ベース）を外部に定義
const HorizontalBarChartComponent = ({ data }: { data: NutritionGoalData[] }) => {
  const chartData = data.map(item => ({
    name: item.label,
    percentage: Math.min(item.percentage, 150), // 表示上限150%
    actualPercentage: item.percentage, // ツールチップ用の実際の値
    current: item.current,
    target: item.target,
    unit: item.unit,
  }));

  // 達成率に応じた色を取得
  const getBarColor = (percentage: number) => {
    if (percentage < 80) return '#eab308'; // 黄色（不足）
    if (percentage <= 100) return '#22c55e'; // 緑（適正）
    return '#ef4444'; // 赤（過剰）
  };

  // カスタムツールチップ
  const CustomHorizontalTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
          <p className="text-sm font-medium mb-2">{label}</p>
          <div className="space-y-1">
            <p className="text-sm">
              現在: <span className="font-medium">{data.current.toFixed(1)} {data.unit}</span>
            </p>
            <p className="text-sm">
              目標: <span className="font-medium">{data.target.toFixed(1)} {data.unit}</span>
            </p>
            <p className="text-sm" style={{ color: getBarColor(data.actualPercentage) }}>
              達成率: <span className="font-bold">{data.actualPercentage.toFixed(1)}%</span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  // カスタムラベル関数
  const renderCustomLabel = (props: any) => {
    const { x, y, width, value, payload } = props;

    // payloadが存在し、必要なプロパティがあることを確認
    if (!payload ||
        typeof payload.actualPercentage !== 'number' ||
        typeof payload.current !== 'number' ||
        !payload.unit) {
      return null;
    }

    return (
      <text
        x={x + width + 5}
        y={y + 15}
        fill="#374151"
        fontSize="12"
        textAnchor="start"
        className="fill-gray-700"
      >
        {`${payload.actualPercentage.toFixed(0)}% (${payload.current.toFixed(1)}${payload.unit})`}
      </text>
    );
  };

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart
        data={chartData}
        layout="horizontal"
        margin={{ top: 5, right: 120, left: 80, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis
          type="number"
          domain={[0, 120]}
          className="text-xs fill-muted-foreground"
          tick={{ fontSize: 12 }}
          tickFormatter={(value) => `${value}%`}
        />
        <YAxis
          type="category"
          dataKey="name"
          className="text-xs fill-muted-foreground"
          tick={{ fontSize: 12 }}
          width={80}
        />
        <Tooltip content={<CustomHorizontalTooltip />} />

        {/* 100%の基準線 */}
        <ReferenceLine x={100} stroke="#94a3b8" strokeDasharray="5 5" strokeWidth={2} />

        {/* メインのバー */}
        <Bar dataKey="percentage">
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={getBarColor(entry.actualPercentage)} />
          ))}
          <LabelList content={renderCustomLabel} />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

export function NutritionGoalChart({
  data,
  chartType = 'bar',
  onChartTypeChange,
  className,
}: NutritionGoalChartProps) {
  if (!data || data.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>目標達成度</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-sm text-muted-foreground">
            目標データがありません
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
        <CardTitle>目標達成度</CardTitle>
        {onChartTypeChange && (
          <Select
            value={chartType}
            onValueChange={(value) => onChartTypeChange(value as 'pie' | 'bar')}
          >
            <SelectTrigger className="w-full sm:w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="bar">棒グラフ</SelectItem>
              <SelectItem value="pie">円グラフ</SelectItem>
            </SelectContent>
          </Select>
        )}
      </CardHeader>
      <CardContent>
        <div className="h-80">
          {chartType === 'pie' ? <PieChartComponent data={data} /> : <HorizontalBarChartComponent data={data} />}
        </div>

        {/* 凡例 */}
        <div className="mt-4 grid grid-cols-3 gap-2 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: '#eab308' }}></div>
            <span>不足 (&lt;80%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: '#22c55e' }}></div>
            <span>適正 (80-100%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: '#ef4444' }}></div>
            <span>過剰 (&gt;100%)</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}