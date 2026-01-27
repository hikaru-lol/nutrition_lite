'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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
  useProfilePageModel,
  type ProfileFormValues,
} from '../model/useProfilePageModel';

const sexLabel: Record<ProfileFormValues['sex'], string> = {
  male: '男性',
  female: '女性',
  other: 'その他',
  undisclosed: '回答しない',
};

export function ProfilePage() {
  const router = useRouter();
  const m = useProfilePageModel();

  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(m.ProfileFormSchema),
    defaultValues: m.defaults,
  });

  useEffect(() => {
    form.reset(m.defaults);
  }, [m.defaults, form]);

  const onSubmit = form.handleSubmit(async (v) => {
    await m.save(v);
    router.push('/target');
  });

  if (m.profileQuery.isLoading)
    return <LoadingState label="プロフィールを読み込み中..." />;

  if (m.profileQuery.isError)
    return (
      <ErrorState
        title="プロフィール取得に失敗"
        message="BFF/Backend の疎通を確認してください。"
      />
    );

  return (
    <div className="space-y-4">
      <div>
        <div className="text-lg font-semibold">プロフィール</div>
        <div className="text-sm text-muted-foreground">
          目標生成に必要な情報を入力します
        </div>
      </div>

      <Card className="p-4">
        <form className="space-y-4" onSubmit={onSubmit}>
          <div className="space-y-2">
            <div className="text-sm font-medium">性別</div>
            <Select
              value={form.watch('sex')}
              onValueChange={(v) =>
                form.setValue('sex', v as ProfileFormValues['sex'])
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="選択" />
              </SelectTrigger>
              <SelectContent>
                {(Object.keys(sexLabel) as Array<ProfileFormValues['sex']>).map(
                  (s) => (
                    <SelectItem key={s} value={s}>
                      {sexLabel[s]}
                    </SelectItem>
                  )
                )}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <div className="text-sm font-medium">生年月日</div>
            <Input type="date" {...form.register('birthdate')} />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <div className="text-sm font-medium">身長 (cm)</div>
              <Input
                type="number"
                inputMode="numeric"
                {...form.register('height_cm')}
              />
            </div>
            <div className="space-y-2">
              <div className="text-sm font-medium">体重 (kg)</div>
              <Input
                type="number"
                inputMode="decimal"
                {...form.register('weight_kg')}
              />
            </div>
          </div>

          <div className="flex items-center justify-end">
            <Button type="submit" disabled={m.upsertMutation.isPending}>
              {m.upsertMutation.isPending ? '保存中...' : '保存して次へ'}
            </Button>
          </div>

          {m.upsertMutation.isError ? (
            <div className="text-sm text-destructive">
              保存に失敗しました。BFF/Backend の profile
              エンドポイントを確認してください。
            </div>
          ) : null}
        </form>
      </Card>
    </div>
  );
}
