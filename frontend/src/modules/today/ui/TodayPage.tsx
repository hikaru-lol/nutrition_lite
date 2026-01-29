'use client';

import { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm, type SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

import { LoadingState } from '@/shared/ui/Status/LoadingState';
import { ErrorState } from '@/shared/ui/Status/ErrorState';

import {
  useTodayPageModel,
  type TodayMealItemFormValues,
} from '../model/useTodayPageModel';

const FormSchema = z.object({
  date: z.string(),
  meal_type: z.enum(['main', 'snack']),
  meal_index: z.number().int().min(1).nullable().optional(),
  name: z.string().min(1),
  amount_value: z.number().nullable().optional(),
  amount_unit: z.string().nullable().optional(),
  serving_count: z.number().nullable().optional(),
  note: z.string().nullable().optional(),
});

export function TodayPage() {
  const router = useRouter();
  const m = useTodayPageModel();

  const [showAdd, setShowAdd] = useState(false);

  const form = useForm<TodayMealItemFormValues>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      date: m.date,
      meal_type: 'main',
      meal_index: 1,
      name: '',
      amount_value: null,
      amount_unit: null,
      serving_count: 1,
      note: null,
    },
  });

  // date が固定なので初回のみでOKだが、安全のため同期
  useMemo(() => {
    form.setValue('date', m.date);
  }, [m.date]); // eslint-disable-line react-hooks/exhaustive-deps

  const onSubmit: SubmitHandler<TodayMealItemFormValues> = async (v) => {
    await m.addMealItem(v);
    form.reset({
      ...form.getValues(),
      name: '',
      note: null,
      amount_value: null,
      amount_unit: null,
      serving_count: 1,
    });
    setShowAdd(false);
  };

  if (m.isLoading) return <LoadingState label="Today を読み込み中..." />;
  if (m.isError)
    return (
      <ErrorState
        title="Today の取得に失敗"
        message="BFF/Backend の疎通を確認してください。"
        onRetry={() => router.refresh()}
      />
    );

  const activeTarget = m.activeTargetQuery.data; // Target | null
  const mealItems = m.mealItemsQuery.data?.items ?? [];

  return (
    <div className="mx-auto w-full max-w-3xl p-6 space-y-6">
      <div className="space-y-1">
        <div className="text-lg font-semibold">Today</div>
        <div className="text-sm text-muted-foreground">日付: {m.date}</div>
      </div>

      {/* Active Target */}
      <Card>
        <CardHeader>
          <CardTitle>アクティブターゲット</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {activeTarget ? (
            <>
              <div className="font-medium">{activeTarget.title}</div>
              <div className="text-sm text-muted-foreground">
                目的: {activeTarget.goal_type} / 活動:{' '}
                {activeTarget.activity_level}
              </div>

              <div className="text-sm">
                栄養素（例: 10件）: {activeTarget.nutrients.length} 件
              </div>

              <Button variant="outline" onClick={() => router.push('/target')}>
                ターゲットを作り直す / 追加する
              </Button>
            </>
          ) : (
            <div className="space-y-3">
              <div className="text-sm text-muted-foreground">
                アクティブターゲットが未設定です。
              </div>
              <Button onClick={() => router.push('/target')}>
                ターゲット作成へ
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Targets List */}
      <Card>
        <CardHeader>
          <CardTitle>ターゲット一覧</CardTitle>
        </CardHeader>
        <CardContent>
          {m.targetsListQuery.isLoading ? (
            <div className="text-sm text-muted-foreground">読み込み中...</div>
          ) : m.targetsListQuery.data?.items.length === 0 ? (
            <div className="text-sm text-muted-foreground">
              ターゲットがありません。
            </div>
          ) : (
            <div className="space-y-3">
              {m.targetsListQuery.data?.items.map((t) => (
                <div
                  key={t.id}
                  className={`flex items-center justify-between rounded-md border p-3 ${
                    t.is_active ? 'border-emerald-500 bg-emerald-50' : ''
                  }`}
                >
                  <div className="space-y-1">
                    <div className="font-medium">
                      {t.title}
                      {t.is_active && (
                        <span className="ml-2 text-xs text-emerald-600">
                          (アクティブ)
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {t.goal_type} / {t.activity_level}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {!t.is_active && (
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={m.activateTargetMutation.isPending}
                        onClick={() => m.activateTargetMutation.mutate(t.id)}
                      >
                        有効化
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={m.deleteTargetMutation.isPending}
                      onClick={() => {
                        if (
                          window.confirm(
                            `「${t.title}」を削除しますか？この操作は取り消せません。`
                          )
                        ) {
                          m.deleteTargetMutation.mutate(t.id);
                        }
                      }}
                    >
                      削除
                    </Button>
                  </div>
                </div>
              ))}
              {m.deleteTargetMutation.isError && (
                <div className="text-sm text-destructive">
                  削除に失敗しました。
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Meals */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>食事ログ</CardTitle>
          <Button variant="outline" onClick={() => setShowAdd((v) => !v)}>
            {showAdd ? '閉じる' : '追加'}
          </Button>
        </CardHeader>

        <CardContent className="space-y-4">
          {showAdd ? (
            <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                <div className="space-y-2">
                  <Label>種別</Label>
                  <Select
                    value={form.watch('meal_type')}
                    onValueChange={(v) =>
                      form.setValue('meal_type', v as 'main' | 'snack', {
                        shouldValidate: true,
                      })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="選択" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="main">メイン</SelectItem>
                      <SelectItem value="snack">間食</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>回数（mainのみ）</Label>
                  <Input
                    type="number"
                    inputMode="numeric"
                    disabled={form.watch('meal_type') === 'snack'}
                    value={form.watch('meal_index') ?? ''}
                    onChange={(e) => {
                      const v = e.target.value;
                      form.setValue('meal_index', v === '' ? null : Number(v), {
                        shouldValidate: true,
                      });
                    }}
                  />
                </div>

                <div className="space-y-2">
                  <Label>食品名</Label>
                  <Input placeholder="例: 白米" {...form.register('name')} />
                  {form.formState.errors.name ? (
                    <p className="text-sm text-destructive">
                      {form.formState.errors.name.message}
                    </p>
                  ) : null}
                </div>

                <div className="space-y-2">
                  <Label>数量</Label>
                  <Input
                    type="number"
                    inputMode="decimal"
                    step="0.1"
                    min="0.1"
                    placeholder="例: 1"
                    value={form.watch('serving_count') ?? ''}
                    onChange={(e) => {
                      const v = e.target.value;
                      form.setValue(
                        'serving_count',
                        v === '' ? null : Number(v),
                        { shouldValidate: true }
                      );
                    }}
                  />
                </div>
              </div>

              <div className="flex items-center justify-end">
                <Button type="submit" disabled={m.createMutation.isPending}>
                  {m.createMutation.isPending ? '追加中...' : '追加'}
                </Button>
              </div>

              {m.createMutation.isError ? (
                <div className="text-sm text-destructive">
                  追加に失敗しました。/meal-items
                  エンドポイントを確認してください。
                </div>
              ) : null}
            </form>
          ) : null}

          <div className="space-y-2">
            {mealItems.length === 0 ? (
              <div className="text-sm text-muted-foreground">
                今日の食事ログはまだありません（0件でOK）。
              </div>
            ) : (
              <div className="space-y-2">
                {mealItems.map((it) => (
                  <div
                    key={it.id}
                    className="flex items-start justify-between rounded-md border p-3"
                  >
                    <div className="space-y-1">
                      <div className="font-medium">{it.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {m.mealTypeLabels[it.meal_type]}
                        {it.meal_type === 'main'
                          ? ` #${it.meal_index ?? 1}`
                          : ''}
                      </div>
                    </div>

                    <Button
                      variant="outline"
                      size="sm"
                      disabled={m.deleteMutation.isPending}
                      onClick={() => m.removeMealItem(it.id)}
                    >
                      削除
                    </Button>
                  </div>
                ))}
              </div>
            )}

            {m.deleteMutation.isError ? (
              <div className="text-sm text-destructive">
                削除に失敗しました。/meal-items/{'{id}'} を確認してください。
              </div>
            ) : null}
          </div>
        </CardContent>
      </Card>

      {/* Card C: 目標達成度 */}
      <Card>
        <CardHeader>
          <CardTitle>目標達成度</CardTitle>
        </CardHeader>
        <CardContent>
          {!activeTarget ? (
            <div className="text-sm text-muted-foreground">
              ターゲットを設定すると達成度が表示されます。
            </div>
          ) : m.dailySummaryQuery.isLoading ? (
            <div className="text-sm text-muted-foreground">計算中...</div>
          ) : m.nutrientProgress.length > 0 ? (
            <div className="space-y-4">
              {m.nutrientProgress.map((np) => {
                // 達成率に応じた色分け
                const percentage = Math.min(np.percentage, 100);
                const isOver = np.percentage > 100;
                const isLow = np.percentage < 50;

                return (
                  <div key={np.code} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{np.label}</span>
                      <span
                        className={
                          isOver
                            ? 'text-amber-600'
                            : isLow
                            ? 'text-muted-foreground'
                            : 'text-emerald-600'
                        }
                      >
                        {np.percentage.toFixed(0)}%
                        <span className="ml-2 text-xs text-muted-foreground">
                          ({np.actual.toFixed(1)} / {np.target.toFixed(1)}{' '}
                          {np.unit})
                        </span>
                      </span>
                    </div>
                    <Progress
                      value={percentage}
                      className={
                        isOver
                          ? '[&>div]:bg-amber-500'
                          : isLow
                          ? '[&>div]:bg-slate-400'
                          : '[&>div]:bg-emerald-500'
                      }
                    />
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-sm text-muted-foreground">
              食事を追加すると達成度が表示されます。
            </div>
          )}
        </CardContent>
      </Card>

      {/* Card E: Daily Report */}
      <Card>
        <CardHeader>
          <CardTitle>日次レポート</CardTitle>
        </CardHeader>
        <CardContent>
          {m.dailyReportQuery.isLoading ? (
            <div className="text-sm text-muted-foreground">読み込み中...</div>
          ) : m.dailyReport ? (
            <div className="space-y-4">
              <div className="text-xs text-muted-foreground">
                作成日時: {m.dailyReport.created_at}
              </div>
              <div>
                <div className="font-medium mb-1">サマリー</div>
                <p className="text-sm">{m.dailyReport.summary}</p>
              </div>
              <div>
                <div className="font-medium mb-1">良かった点</div>
                <ul className="list-disc list-inside text-sm space-y-1">
                  {m.dailyReport.good_points.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>
              </div>
              <div>
                <div className="font-medium mb-1">改善点</div>
                <ul className="list-disc list-inside text-sm space-y-1">
                  {m.dailyReport.improvement_points.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>
              </div>
              <div>
                <div className="font-medium mb-1">明日のフォーカス</div>
                <ul className="list-disc list-inside text-sm space-y-1">
                  {m.dailyReport.tomorrow_focus.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="text-sm text-muted-foreground">
                日次レポートがまだ生成されていません。
              </div>
              <Button
                onClick={() => m.generateReportMutation.mutate()}
                disabled={m.generateReportMutation.isPending}
              >
                {m.generateReportMutation.isPending
                  ? 'レポート生成中...'
                  : 'レポートを生成する'}
              </Button>
              {m.generateReportMutation.isError ? (
                <div className="text-sm text-destructive">
                  レポート生成に失敗しました。食事ログが完了しているか確認してください。
                </div>
              ) : null}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
