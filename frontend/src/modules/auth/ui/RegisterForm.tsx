'use client';

import { z } from 'zod';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

import { useRegisterPageModel } from '../model/useRegisterPageModel';

const schema = z
  .object({
    email: z.string().email('メールアドレス形式で入力してください'),
    password: z.string().min(8, 'パスワードは8文字以上にしてください'),
    confirmPassword: z.string().min(1, '確認用パスワードを入力してください'),
  })
  .refine((v) => v.password === v.confirmPassword, {
    path: ['confirmPassword'],
    message: 'パスワードが一致しません',
  });

type Form = z.infer<typeof schema>;

export function RegisterForm(props: { onSuccess?: () => void }) {
  const m = useRegisterPageModel();
  const form = useForm<Form>({
    resolver: zodResolver(schema),
    defaultValues: { email: '', password: '', confirmPassword: '' },
  });

  const onSubmit = async (v: Form) => {
    await m.submit({ email: v.email, password: v.password });
    props.onSuccess?.();
  };

  const submitting = m.state.type === 'submitting';

  return (
    <Card className="w-full max-w-sm">
      <CardHeader>
        <CardTitle>新規登録</CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" {...form.register('email')} />
          {form.formState.errors.email ? (
            <p className="text-sm text-destructive">
              {form.formState.errors.email.message}
            </p>
          ) : null}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input id="password" type="password" {...form.register('password')} />
          {form.formState.errors.password ? (
            <p className="text-sm text-destructive">
              {form.formState.errors.password.message}
            </p>
          ) : null}
        </div>

        <div className="space-y-2">
          <Label htmlFor="confirmPassword">Confirm Password</Label>
          <Input
            id="confirmPassword"
            type="password"
            {...form.register('confirmPassword')}
          />
          {form.formState.errors.confirmPassword ? (
            <p className="text-sm text-destructive">
              {form.formState.errors.confirmPassword.message}
            </p>
          ) : null}
        </div>

        {m.state.type === 'error' ? (
          <p className="text-sm text-destructive whitespace-pre-wrap">
            {m.state.message}
          </p>
        ) : null}

        {m.state.type === 'success' ? (
          <p className="text-sm text-muted-foreground">
            登録が完了しました。ログインしてください。
          </p>
        ) : null}

        <Button
          className="w-full"
          disabled={submitting}
          onClick={form.handleSubmit(onSubmit)}
        >
          {submitting ? '登録中…' : '登録'}
        </Button>

        <div className="text-sm text-muted-foreground">
          すでにアカウントがありますか？{' '}
          <Link className="underline" href="/auth/login">
            ログインへ
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
