import { z } from 'zod';

// ログイン用スキーマ
export const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'メールアドレスを入力してください')
    .email('正しいメールアドレス形式で入力してください'),
  password: z.string().min(1, 'パスワードを入力してください'),
});

export type LoginInput = z.infer<typeof loginSchema>;

// 新規登録用スキーマ
export const registerSchema = z.object({
  name: z.string().optional(),
  email: z
    .string()
    .min(1, 'メールアドレスを入力してください')
    .email('正しいメールアドレス形式で入力してください'),
  password: z.string().min(8, 'パスワードは8文字以上で入力してください'),
});

export type RegisterInput = z.infer<typeof registerSchema>;
