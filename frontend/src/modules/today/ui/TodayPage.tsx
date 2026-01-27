'use client';

import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

import { LoadingState } from '@/shared/ui/Status/LoadingState';
import { ErrorState } from '@/shared/ui/Status/ErrorState';

import { useTodayPageModel } from '../model/useTodayPageModel';

export function TodayPage() {
  const m = useTodayPageModel();

  if (m.todayQuery.isLoading) {
    return <LoadingState label="今日のデータを読み込み中..." />;
  }

  if (m.todayQuery.isError) {
    return (
      <ErrorState
        title="Todayの取得に失敗"
        message="BFF/Backend の today エンドポイントを確認してください。"
      />
    );
  }

  const data = m.todayQuery.data!;

  return (
    <div className="space-y-4 p-6">
      <div className="space-y-1">
        <div className="text-lg font-semibold">Today</div>
        <div className="text-sm text-muted-foreground">
          今日の食事記録と目標のサマリー
        </div>
      </div>

      <Card className="p-4 space-y-3">
        <div className="text-sm font-medium">日付</div>
        <Input
          type="date"
          value={m.selectedDate}
          onChange={(e) => m.setSelectedDate(e.target.value)}
        />
      </Card>

      <Card className="p-4 space-y-2">
        <div className="text-sm font-medium">アクティブ目標</div>
        {data.active_target ? (
          <div className="text-sm">
            <div className="font-semibold">{data.active_target.title}</div>
            <div className="text-muted-foreground">
              目標タイプ: {data.active_target.goal_type}
            </div>
          </div>
        ) : (
          <div className="text-sm text-muted-foreground">
            目標が未設定です（Target作成が必要）
          </div>
        )}
      </Card>

      <Card className="p-4 space-y-2">
        <div className="text-sm font-medium">今日の食事</div>

        {data.meals.length === 0 ? (
          <div className="text-sm text-muted-foreground">
            まだ食事記録がありません
          </div>
        ) : (
          <ul className="space-y-2">
            {data.meals.map((x) => (
              <li key={x.id} className="text-sm">
                <span className="font-medium">{x.meal_type}</span>
                {x.meal_index != null ? ` (${x.meal_index})` : ''}
                {' · '}
                {x.name}
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
