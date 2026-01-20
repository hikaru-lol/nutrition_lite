// frontend/components/meals/MealNutritionChart.tsx
'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { NutritionNutrientIntakeApi } from '@/lib/api/nutrition';

type MealNutritionChartProps = {
  nutrients: NutritionNutrientIntakeApi[];
  height?: number;
  title?: string;
};

const LABEL_MAP: Record<string, string> = {
  carbohydrate: '炭水化物',
  protein: 'たんぱく質',
  fat: '脂質',
  water: '水分',
  fiber: '食物繊維',
  sodium: 'ナトリウム',
  iron: '鉄',
  calcium: 'カルシウム',
  vitamin_d: 'ビタミンD',
  potassium: 'カリウム',
};

export function MealNutritionChart({
  nutrients,
  height = 220,
  title,
}: MealNutritionChartProps) {
  // グラフ用データに変換
  const data = nutrients.map((n) => ({
    name: LABEL_MAP[n.code] ?? n.code,
    value: n.amount,
    unit: n.unit,
  }));

  if (data.length === 0) {
    return (
      <p className="text-xs text-slate-500">
        まだ栄養情報がありません。「栄養を計算」ボタンを押して生成してください。
      </p>
    );
  }

  return (
    <div className="mt-3">
      {title && (
        <p className="mb-2 text-xs font-semibold text-slate-300">{title}</p>
      )}
      <div style={{ width: '100%', height }}>
        <ResponsiveContainer>
          <BarChart
            data={data}
            margin={{ top: 10, right: 10, left: 0, bottom: 20 }}
          >
            <XAxis
              dataKey="name"
              tick={{ fontSize: 10, fill: '#9ca3af' }}
              interval={0}
              angle={-20}
              textAnchor="end"
              height={50}
            />
            <YAxis tick={{ fontSize: 10, fill: '#9ca3af' }} tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#020617',
                border: '1px solid #1f2937',
                borderRadius: 8,
                fontSize: 12,
              }}
              formatter={(value: any, _name, props) => [
                `${value}${(props?.payload as any)?.unit ?? ''}`,
                (props?.payload as any)?.name ?? '',
              ]}
            />
            <Bar
              dataKey="value"
              // デザインシステムに合わせてエメラルド系
              fill="#22c55e"
              radius={[6, 6, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
