// frontend/components/auth/RegisterForm.tsx
'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';

export type RegisterFormValues = {
  name: string;
  email: string;
  password: string;
};

export type RegisterFormProps = {
  onSubmit: (values: RegisterFormValues) => Promise<void> | void;
  isSubmitting?: boolean;
  serverError?: string | null;
};

export function RegisterForm({
  onSubmit,
  isSubmitting = false,
  serverError,
}: RegisterFormProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fieldError, setFieldError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !password) {
      setFieldError('メールアドレスとパスワードを入力してください。');
      return;
    }

    setFieldError(null);
    await onSubmit({ name, email, password });
  };

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      {(fieldError || serverError) && (
        <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/40 rounded-lg px-3 py-2">
          {fieldError || serverError}
        </p>
      )}

      <div>
        <Label htmlFor="name">名前（任意）</Label>
        <Input
          id="name"
          placeholder="山田 太郎"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>

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
          autoComplete="new-password"
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
        {isSubmitting ? '登録中...' : '登録してはじめる'}
      </Button>
    </form>
  );
}
