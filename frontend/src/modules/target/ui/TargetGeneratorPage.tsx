'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useForm, type SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

import {
  useTargetGeneratorPageModel,
  type TargetFormValues,
} from '../model/useTargetGeneratorPageModel';
import { TutorialTrigger } from '@/modules/tutorial';

export function TargetGeneratorPage() {
  const router = useRouter();
  const m = useTargetGeneratorPageModel();

  const form = useForm<TargetFormValues>({
    resolver: zodResolver(m.TargetFormSchema),
    defaultValues: m.defaultFormValues,
  });

  // 成功したら /today へ遷移
  useEffect(() => {
    if (m.state.type === 'success') {
      router.replace('/today');
    }
  }, [m.state.type, router]);

  const onSubmit: SubmitHandler<TargetFormValues> = async (v) => {
    await m.submit(v);
  };

  const isSubmitting = m.state.type === 'submitting';

  return (
    <div className="w-full max-w-2xl space-y-4">
      <div data-tour="target-title">
        <div className="flex items-center gap-2">
          <div className="text-lg font-semibold">ターゲット生成</div>
          <TutorialTrigger tutorialId="onboarding_target" className="ml-auto" />
        </div>
        <div className="text-sm text-muted-foreground">
          目標に合わせた栄養ターゲットを自動生成します
        </div>
      </div>

      <Card className="p-4">
        <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
          {/* タイトル */}
          <div className="space-y-2" data-tour="target-title-field">
            <div className="text-sm font-medium">タイトル</div>
            <Input
              placeholder="例: ダイエット2026"
              {...form.register('title')}
            />
            {form.formState.errors.title ? (
              <p className="text-sm text-destructive">
                {form.formState.errors.title.message}
              </p>
            ) : null}
          </div>

          {/* 目標タイプ */}
          <div className="space-y-2" data-tour="target-goal-type">
            <div className="text-sm font-medium">目標タイプ</div>
            <Select
              value={form.watch('goal_type')}
              onValueChange={(v) =>
                form.setValue('goal_type', v as TargetFormValues['goal_type'])
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="選択" />
              </SelectTrigger>
              <SelectContent>
                {(
                  Object.keys(m.goalTypeLabels) as Array<
                    TargetFormValues['goal_type']
                  >
                ).map((key) => (
                  <SelectItem key={key} value={key}>
                    {m.goalTypeLabels[key]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 活動レベル */}
          <div className="space-y-2" data-tour="target-activity-level">
            <div className="text-sm font-medium">活動レベル</div>
            <Select
              value={form.watch('activity_level')}
              onValueChange={(v) =>
                form.setValue(
                  'activity_level',
                  v as TargetFormValues['activity_level']
                )
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="選択" />
              </SelectTrigger>
              <SelectContent>
                {(
                  Object.keys(m.activityLevelLabels) as Array<
                    TargetFormValues['activity_level']
                  >
                ).map((key) => (
                  <SelectItem key={key} value={key}>
                    {m.activityLevelLabels[key]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 目標の詳細（任意） */}
          <div className="space-y-2" data-tour="target-description">
            <div className="text-sm font-medium">目標の詳細（任意）</div>
            <Textarea
              placeholder="例: 3ヶ月で5kg減量したい"
              rows={3}
              {...form.register('goal_description')}
            />
          </div>

          {/* 送信ボタン */}
          <div className="flex items-center justify-end" data-tour="target-submit">
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? '生成中...' : 'ターゲットを生成'}
            </Button>
          </div>

          {/* エラー表示 */}
          {m.state.type === 'error' ? (
            <div className="text-sm text-destructive">{m.state.message}</div>
          ) : null}
        </form>
      </Card>
    </div>
  );
}
