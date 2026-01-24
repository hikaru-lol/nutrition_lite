'use client';

import { useForm, type SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

import { useTargetGeneratorPageModel } from '../model/useTargetGeneratorPageModel';
import {
  generateTargetRequestSchema,
  type GenerateTargetRequest,
} from '../contract/targetContract';

export function TargetGeneratorPage() {
  const m = useTargetGeneratorPageModel();

  const form = useForm<GenerateTargetRequest>({
    resolver: zodResolver(generateTargetRequestSchema),
    defaultValues: {
      sex: 'male',
      age: 30,
      heightCm: 170,
      weightKg: 65,
      activityLevel: 'moderate',
      goal: 'maintain',
    },
  });

  const onSubmit: SubmitHandler<GenerateTargetRequest> = async (v) => {
    await m.submit(v); // ✅ cast不要
  };

  const disabled = m.state.type === 'submitting';

  return (
    <div className="mx-auto w-full max-w-2xl p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>ターゲット生成</CardTitle>
        </CardHeader>

        <CardContent className="space-y-6">
          <form className="space-y-5" onSubmit={form.handleSubmit(onSubmit)}>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>性別</Label>
                <Select
                  value={form.watch('sex')}
                  onValueChange={(v) =>
                    form.setValue('sex', v as GenerateTargetRequest['sex'], {
                      shouldValidate: true,
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="選択" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="male">男性</SelectItem>
                    <SelectItem value="female">女性</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="age">年齢</Label>
                <Input
                  id="age"
                  type="number"
                  inputMode="numeric"
                  {...form.register('age', { valueAsNumber: true })}
                />
                {form.formState.errors.age ? (
                  <p className="text-sm text-destructive">
                    {form.formState.errors.age.message}
                  </p>
                ) : null}
              </div>

              <div className="space-y-2">
                <Label htmlFor="heightCm">身長 (cm)</Label>
                <Input
                  id="heightCm"
                  type="number"
                  inputMode="numeric"
                  {...form.register('heightCm', { valueAsNumber: true })}
                />
                {form.formState.errors.heightCm ? (
                  <p className="text-sm text-destructive">
                    {form.formState.errors.heightCm.message}
                  </p>
                ) : null}
              </div>

              <div className="space-y-2">
                <Label htmlFor="weightKg">体重 (kg)</Label>
                <Input
                  id="weightKg"
                  type="number"
                  inputMode="decimal"
                  {...form.register('weightKg', { valueAsNumber: true })}
                />
                {form.formState.errors.weightKg ? (
                  <p className="text-sm text-destructive">
                    {form.formState.errors.weightKg.message}
                  </p>
                ) : null}
              </div>

              <div className="space-y-2">
                <Label>活動レベル</Label>
                <Select
                  value={form.watch('activityLevel')}
                  onValueChange={(v) =>
                    form.setValue(
                      'activityLevel',
                      v as GenerateTargetRequest['activityLevel'],
                      { shouldValidate: true }
                    )
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="選択" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sedentary">
                      低い（ほぼ運動しない）
                    </SelectItem>
                    <SelectItem value="light">やや低い（週1〜2）</SelectItem>
                    <SelectItem value="moderate">普通（週3〜4）</SelectItem>
                    <SelectItem value="active">高い（週5〜6）</SelectItem>
                    <SelectItem value="very_active">
                      非常に高い（毎日）
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>目的</Label>
                <Select
                  value={form.watch('goal')}
                  onValueChange={(v) =>
                    form.setValue('goal', v as GenerateTargetRequest['goal'], {
                      shouldValidate: true,
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="選択" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="lose">減量</SelectItem>
                    <SelectItem value="maintain">維持</SelectItem>
                    <SelectItem value="gain">増量</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {m.state.type === 'error' ? (
              <p className="text-sm text-destructive whitespace-pre-wrap">
                {m.state.message}
              </p>
            ) : null}

            <Button className="w-full" type="submit" disabled={disabled}>
              {disabled ? '生成中…' : 'ターゲットを生成'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* 結果表示はそのままでOK */}
    </div>
  );
}
