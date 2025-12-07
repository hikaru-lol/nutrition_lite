'use client';

import * as React from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';

export type LoginFormValues = {
  email: string;
  password: string;
};

export type LoginFormProps = {
  onSubmit: (values: LoginFormValues) => Promise<void> | void;
  isSubmitting?: boolean;
  serverError?: string | null;
};

export function LoginForm({
  onSubmit,
  isSubmitting = false,
  serverError,
}: LoginFormProps) {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [fieldError, setFieldError] = React.useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // 簡易バリデーション
    if (!email || !password) {
      setFieldError('メールアドレスとパスワードを入力してください。');
      return;
    }

    setFieldError(null);
    await onSubmit({ email, password });
  };

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      {fieldError && (
        <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/40 rounded-lg px-3 py-2">
          {fieldError}
        </p>
      )}
      {serverError && (
        <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/40 rounded-lg px-3 py-2">
          {serverError}
        </p>
      )}

      <div>
        <Label htmlFor="email">メールアドレス</Label>
        <Input
          id="email"
          type="email"
          autoComplete="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>

      <div>
        <Label htmlFor="password">パスワード</Label>
        <Input
          id="password"
          type="password"
          autoComplete="current-password"
          placeholder="********"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>

      <Button
        type="submit"
        className="w-full"
        size="md"
        disabled={isSubmitting}
      >
        {isSubmitting ? 'ログイン中...' : 'ログイン'}
      </Button>
    </form>
  );
}
