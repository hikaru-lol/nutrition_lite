'use client';

import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Edit, User, Calendar, Scale, Ruler, Save, X, UtensilsCrossed } from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

import { LoadingState } from '@/shared/ui/Status/LoadingState';
import { ErrorState } from '@/shared/ui/Status/ErrorState';

import { useProfileEditPageModel } from '../model/useProfileEditPageModel';
import {
  ProfileFormSchema,
  type ProfileFormValues,
} from '../model/useProfilePageModel';

const sexLabels: Record<ProfileFormValues['sex'], string> = {
  male: '男性',
  female: '女性',
  other: 'その他',
  undisclosed: '回答しない',
};

export function ProfileEditPage() {
  const m = useProfileEditPageModel();

  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(ProfileFormSchema),
    defaultValues: m.defaults,
  });

  // データが更新されたらフォームをリセット
  useEffect(() => {
    if (m.profileQuery.isSuccess && m.profileQuery.data && !m.isEditing) {
      form.reset(m.defaults);
    }
  }, [m.profileQuery.isSuccess, m.profileQuery.data, m.defaults, form.reset, m.isEditing]);

  const onSubmit = form.handleSubmit(async (values) => {
    await m.save(values);
  });

  const handleCancel = () => {
    form.reset(m.defaults);
    m.cancelEditing();
  };

  if (m.profileQuery.isLoading) {
    return <LoadingState label="プロフィールを読み込み中..." />;
  }

  if (m.profileQuery.isError) {
    return (
      <ErrorState
        title="プロフィール取得に失敗"
        message="BFF/Backend の疎通を確認してください。"
        onRetry={() => m.profileQuery.refetch()}
      />
    );
  }

  const profile = m.profileQuery.data;

  if (!profile) {
    return (
      <div className="w-full space-y-6">
        <div>
          <h1 className="text-2xl font-bold">設定</h1>
          <p className="text-muted-foreground">プロフィール情報を管理します</p>
        </div>
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center">
              <User className="h-12 w-12 mx-auto mb-3 text-muted-foreground" />
              <p className="text-muted-foreground">
                プロフィールが見つかりません
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // 年齢計算
  const calculateAge = (birthdate: string): number => {
    const today = new Date();
    const birth = new Date(birthdate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  return (
    <div className="w-full space-y-6">
      {/* ページヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">設定</h1>
          <p className="text-muted-foreground">プロフィール情報を確認・編集できます</p>
        </div>
        {!m.isEditing && (
          <Button onClick={m.startEditing} className="gap-2">
            <Edit className="h-4 w-4" />
            編集
          </Button>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            基本情報
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!m.isEditing ? (
            /* 表示モード */
            <div className="space-y-6">
              {/* 基本情報表示 */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
                {/* 性別 */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <User className="h-4 w-4" />
                    性別
                  </div>
                  <Badge variant="outline" className="justify-start">
                    {sexLabels[profile.sex as keyof typeof sexLabels]}
                  </Badge>
                </div>

                {/* 生年月日・年齢 */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Calendar className="h-4 w-4" />
                    生年月日
                  </div>
                  <div>
                    <div className="font-medium">
                      {new Date(profile.birthdate).toLocaleDateString('ja-JP')}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {calculateAge(profile.birthdate)}歳
                    </div>
                  </div>
                </div>

                {/* 身長 */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Ruler className="h-4 w-4" />
                    身長
                  </div>
                  <div className="font-medium">{profile.height_cm}cm</div>
                </div>

                {/* 体重 */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Scale className="h-4 w-4" />
                    体重
                  </div>
                  <div className="font-medium">{profile.weight_kg}kg</div>
                </div>

                {/* 1日の食事回数 */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <UtensilsCrossed className="h-4 w-4" />
                    食事回数
                  </div>
                  <div className="font-medium">{profile.meals_per_day ?? 3}回/日</div>
                </div>
              </div>

              {/* BMI表示 */}
              <div className="bg-muted/50 rounded-lg p-4">
                <h3 className="font-medium mb-2">BMI</h3>
                <div className="text-2xl font-bold">
                  {(profile.weight_kg / Math.pow(profile.height_cm / 100, 2)).toFixed(1)}
                </div>
                <div className="text-sm text-muted-foreground">
                  身長 {profile.height_cm}cm・体重 {profile.weight_kg}kg から算出
                </div>
              </div>
            </div>
          ) : (
            /* 編集モード */
            <form onSubmit={onSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 性別 */}
                <div className="space-y-2">
                  <Label htmlFor="sex">性別</Label>
                  <Select
                    value={form.watch('sex')}
                    onValueChange={(v) =>
                      form.setValue('sex', v as ProfileFormValues['sex'])
                    }
                    disabled={m.saveMutation.isPending}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="選択" />
                    </SelectTrigger>
                    <SelectContent>
                      {(Object.keys(sexLabels) as Array<ProfileFormValues['sex']>).map(
                        (key) => (
                          <SelectItem key={key} value={key}>
                            {sexLabels[key]}
                          </SelectItem>
                        )
                      )}
                    </SelectContent>
                  </Select>
                  {form.formState.errors.sex && (
                    <p className="text-sm text-destructive">
                      {form.formState.errors.sex.message}
                    </p>
                  )}
                </div>

                {/* 生年月日 */}
                <div className="space-y-2">
                  <Label htmlFor="birthdate">生年月日</Label>
                  <Input
                    id="birthdate"
                    type="date"
                    {...form.register('birthdate')}
                    disabled={m.saveMutation.isPending}
                  />
                  {form.formState.errors.birthdate && (
                    <p className="text-sm text-destructive">
                      {form.formState.errors.birthdate.message}
                    </p>
                  )}
                </div>

                {/* 身長 */}
                <div className="space-y-2">
                  <Label htmlFor="height_cm">身長 (cm)</Label>
                  <Input
                    id="height_cm"
                    type="number"
                    inputMode="numeric"
                    min="50"
                    max="250"
                    {...form.register('height_cm')}
                    disabled={m.saveMutation.isPending}
                  />
                  {form.formState.errors.height_cm && (
                    <p className="text-sm text-destructive">
                      {form.formState.errors.height_cm.message}
                    </p>
                  )}
                </div>

                {/* 体重 */}
                <div className="space-y-2">
                  <Label htmlFor="weight_kg">体重 (kg)</Label>
                  <Input
                    id="weight_kg"
                    type="number"
                    inputMode="decimal"
                    min="20"
                    max="300"
                    step="0.1"
                    {...form.register('weight_kg')}
                    disabled={m.saveMutation.isPending}
                  />
                  {form.formState.errors.weight_kg && (
                    <p className="text-sm text-destructive">
                      {form.formState.errors.weight_kg.message}
                    </p>
                  )}
                </div>

                {/* 1日の食事回数 */}
                <div className="space-y-2">
                  <Label htmlFor="meals_per_day">1日の食事回数</Label>
                  <Select
                    value={(form.watch('meals_per_day') ?? 3).toString()}
                    onValueChange={(v) =>
                      form.setValue('meals_per_day', parseInt(v, 10))
                    }
                    disabled={m.saveMutation.isPending}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="選択" />
                    </SelectTrigger>
                    <SelectContent>
                      {[1, 2, 3, 4, 5, 6].map((count) => (
                        <SelectItem key={count} value={count.toString()}>
                          {count}回
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {form.formState.errors.meals_per_day && (
                    <p className="text-sm text-destructive">
                      {form.formState.errors.meals_per_day.message}
                    </p>
                  )}
                </div>
              </div>

              {/* アクションボタン */}
              <div className="flex items-center justify-end gap-3 pt-4 border-t">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleCancel}
                  disabled={m.saveMutation.isPending}
                  className="gap-2"
                >
                  <X className="h-4 w-4" />
                  キャンセル
                </Button>
                <Button
                  type="submit"
                  disabled={m.saveMutation.isPending}
                  className="gap-2"
                >
                  <Save className="h-4 w-4" />
                  {m.saveMutation.isPending ? '保存中...' : '保存'}
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}