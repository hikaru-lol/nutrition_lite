'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { List, Target, Play, Trash2, Calendar, Zap, MapPin } from 'lucide-react';

import type { Target as TargetType } from '../contract/targetContract';

interface TargetListCardProps {
  targets: TargetType[];
  activeTargetId: string | null;
  isLoading?: boolean;
  isActivating?: boolean;
  isDeleting?: boolean;
  onActivate: (id: string) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
}

const goalTypeLabels: Record<string, string> = {
  weight_loss: '減量',
  maintain: '維持',
  weight_gain: '増量',
  health_improve: '健康改善',
};

const activityLevelLabels: Record<string, string> = {
  low: '低',
  normal: '中',
  high: '高',
};

export function TargetListCard({
  targets,
  activeTargetId,
  isLoading,
  isActivating,
  isDeleting,
  onActivate,
  onDelete,
}: TargetListCardProps) {
  const [selectedTargetId, setSelectedTargetId] = useState<string | null>(null);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <List className="h-5 w-5" />
            全てのターゲット
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="border rounded-lg p-4">
                <div className="h-4 bg-muted rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-muted rounded w-1/2"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (targets.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <List className="h-5 w-5" />
            全てのターゲット
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Target className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p>まだターゲットが作成されていません</p>
            <p className="text-sm">最初のターゲットを作成しましょう</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const handleActivate = async (id: string) => {
    setSelectedTargetId(id);
    await onActivate(id);
    setSelectedTargetId(null);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('このターゲットを削除しますか？')) {
      setSelectedTargetId(id);
      await onDelete(id);
      setSelectedTargetId(null);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <List className="h-5 w-5" />
          全てのターゲット ({targets.length})
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {targets.map((target) => {
          const isActive = target.id === activeTargetId;
          const isProcessing = selectedTargetId === target.id && (isActivating || isDeleting);

          // カロリー計算
          const protein = target.nutrients.find(n => n.code === 'protein');
          const fat = target.nutrients.find(n => n.code === 'fat');
          const carbohydrate = target.nutrients.find(n => n.code === 'carbohydrate');
          const totalCalories = Math.round(
            ((protein?.amount ?? 0) * 4) +
            ((fat?.amount ?? 0) * 9) +
            ((carbohydrate?.amount ?? 0) * 4)
          );

          return (
            <div
              key={target.id}
              className={`border rounded-lg p-4 transition-colors ${
                isActive
                  ? 'border-primary bg-primary/5'
                  : 'border-border hover:border-muted-foreground'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  {/* ターゲット基本情報 */}
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-medium truncate">{target.title}</h3>
                    {isActive && (
                      <Badge variant="default" className="text-xs">
                        アクティブ
                      </Badge>
                    )}
                  </div>

                  {/* 詳細情報 */}
                  <div className="flex items-center gap-4 text-sm text-muted-foreground mb-2">
                    <div className="flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      {goalTypeLabels[target.goal_type]}
                    </div>
                    <div className="flex items-center gap-1">
                      <Zap className="h-3 w-3" />
                      活動: {activityLevelLabels[target.activity_level]}
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {new Date(target.created_at).toLocaleDateString('ja-JP')}
                    </div>
                  </div>

                  {/* カロリー目標 */}
                  <div className="text-sm">
                    <span className="font-medium">{totalCalories.toLocaleString()}kcal/日</span>
                    <span className="text-muted-foreground ml-2">
                      P:{protein?.amount?.toFixed(0) ?? '0'}g
                      F:{fat?.amount?.toFixed(0) ?? '0'}g
                      C:{carbohydrate?.amount?.toFixed(0) ?? '0'}g
                    </span>
                  </div>

                  {/* 目標詳細（あれば） */}
                  {target.goal_description && (
                    <div className="text-xs text-muted-foreground italic mt-1 truncate">
                      "{target.goal_description}"
                    </div>
                  )}
                </div>

                {/* アクション */}
                <div className="flex items-center gap-2 ml-4">
                  {!isActive && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleActivate(target.id)}
                      disabled={isProcessing}
                      className="text-xs"
                    >
                      <Play className="h-3 w-3 mr-1" />
                      {isProcessing && isActivating ? '有効化中...' : '有効化'}
                    </Button>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(target.id)}
                    disabled={isProcessing}
                    className="text-xs text-destructive hover:text-destructive"
                  >
                    <Trash2 className="h-3 w-3 mr-1" />
                    {isProcessing && isDeleting ? '削除中...' : '削除'}
                  </Button>
                </div>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}