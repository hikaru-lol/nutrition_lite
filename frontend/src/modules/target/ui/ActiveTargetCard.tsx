'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Target, MapPin, Calendar, Zap } from 'lucide-react';

import type { Target as TargetType } from '../contract/targetContract';

interface ActiveTargetCardProps {
  target: TargetType | null;
  isLoading?: boolean;
}

const goalTypeLabels: Record<string, string> = {
  weight_loss: '減量',
  maintain: '維持',
  weight_gain: '増量',
  health_improve: '健康改善',
};

const activityLevelLabels: Record<string, string> = {
  low: '低い',
  normal: '普通',
  high: '高い',
};

export function ActiveTargetCard({ target, isLoading }: ActiveTargetCardProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            アクティブターゲット
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-3">
            <div className="h-4 bg-muted rounded w-3/4"></div>
            <div className="h-4 bg-muted rounded w-1/2"></div>
            <div className="h-20 bg-muted rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!target) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            アクティブターゲット
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Target className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p>アクティブなターゲットがありません</p>
            <p className="text-sm">新規作成してターゲットを設定しましょう</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // 主要栄養素を計算（P/F/C + カロリー）
  const protein = target.nutrients.find(n => n.code === 'protein');
  const fat = target.nutrients.find(n => n.code === 'fat');
  const carbohydrate = target.nutrients.find(n => n.code === 'carbohydrate');

  // カロリー計算 (P: 4kcal/g, F: 9kcal/g, C: 4kcal/g)
  const totalCalories = Math.round(
    ((protein?.amount ?? 0) * 4) +
    ((fat?.amount ?? 0) * 9) +
    ((carbohydrate?.amount ?? 0) * 4)
  );

  return (
    <Card className="border-primary/20">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-primary" />
            アクティブターゲット
          </CardTitle>
          <Badge variant="default" className="bg-green-100 text-green-800">
            有効
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* ターゲット基本情報 */}
        <div>
          <h3 className="font-semibold text-lg">{target.title}</h3>
          <div className="flex items-center gap-4 text-sm text-muted-foreground mt-2">
            <div className="flex items-center gap-1">
              <MapPin className="h-4 w-4" />
              {goalTypeLabels[target.goal_type]}
            </div>
            <div className="flex items-center gap-1">
              <Zap className="h-4 w-4" />
              活動レベル: {activityLevelLabels[target.activity_level]}
            </div>
            <div className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              {new Date(target.created_at).toLocaleDateString('ja-JP')}
            </div>
          </div>
        </div>

        {/* 目標詳細 */}
        {target.goal_description && (
          <div>
            <p className="text-sm text-muted-foreground italic">
              "{target.goal_description}"
            </p>
          </div>
        )}

        {/* カロリー・PFC目標 */}
        <div className="bg-muted/30 rounded-lg p-4">
          <div className="grid grid-cols-2 gap-4">
            {/* カロリー目標 */}
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">
                {totalCalories.toLocaleString()}
              </div>
              <div className="text-sm text-muted-foreground">kcal/日</div>
            </div>

            {/* PFCバランス */}
            <div className="space-y-2">
              <div className="text-sm font-medium">PFC目標 (g/日)</div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-green-600">タンパク質</span>
                  <span className="font-mono">{protein?.amount?.toFixed(1) ?? '0'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-yellow-600">脂質</span>
                  <span className="font-mono">{fat?.amount?.toFixed(1) ?? '0'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-blue-600">炭水化物</span>
                  <span className="font-mono">{carbohydrate?.amount?.toFixed(1) ?? '0'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* LLM根拠 */}
        {target.llm_rationale && (
          <details className="cursor-pointer">
            <summary className="text-sm font-medium text-muted-foreground hover:text-foreground">
              AI設定理由を表示
            </summary>
            <div className="mt-2 text-sm text-muted-foreground bg-muted/50 rounded p-3">
              {target.llm_rationale}
            </div>
          </details>
        )}
      </CardContent>
    </Card>
  );
}