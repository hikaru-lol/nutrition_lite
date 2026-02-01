'use client';

import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

import { useLoginPageModel } from '../model/useLoginPageModel';

const schema = z.object({
  email: z.string().email('メールアドレス形式で入力してください'),
  password: z.string().min(1, 'パスワードを入力してください'),
});
type Form = z.infer<typeof schema>;

export function LoginForm(props: { onSuccess?: () => void }) {
  const m = useLoginPageModel();
  const form = useForm<Form>({
    resolver: zodResolver(schema),
    defaultValues: { email: '', password: '' },
  });

  const onSubmit = async (v: Form) => {
    await m.submit(v);
    props.onSuccess?.();
  };

  return (
    <Card className="w-full max-w-sm">
      <CardHeader>
        <CardTitle>ログイン</CardTitle>
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

        {m.errorMessage ? (
          <p className="text-sm text-destructive whitespace-pre-wrap">
            {m.errorMessage}
          </p>
        ) : null}

        <Button
          className="w-full"
          disabled={m.isSubmitting}
          onClick={form.handleSubmit(onSubmit)}
        >
          {m.isSubmitting ? 'ログイン中…' : 'ログイン'}
        </Button>
      </CardContent>
    </Card>
  );
}
