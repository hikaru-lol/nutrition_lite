'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';

import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/shared/ui/form';

import { RegisterInput, registerSchema } from '../model/schema';
import { useRegister } from '../hooks/useMe';

export const RegisterForm = () => {
  const router = useRouter();
  const { mutate: register, isPending, error } = useRegister();

  const form = useForm<RegisterInput>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: '',
      email: '',
      password: '',
    },
  });

  const onSubmit = (data: RegisterInput) => {
    register(data, {
      onSuccess: () => {
        // 登録成功後はオンボーディング（プロフィール設定）へ遷移するのが一般的
        // 今回はとりあえずMealsへ
        router.push('/onboarding/profile');
      },
    });
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>お名前 (任意)</FormLabel>
              <FormControl>
                <Input placeholder="Taro Yamada" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>メールアドレス</FormLabel>
              <FormControl>
                <Input placeholder="your@email.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>パスワード</FormLabel>
              <FormControl>
                <Input type="password" placeholder="8文字以上" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {error && (
          <div className="text-sm text-red-500 font-medium">
            登録に失敗しました。既に使用されているメールアドレスの可能性があります。
          </div>
        )}

        <Button type="submit" className="w-full" disabled={isPending}>
          {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          アカウント作成
        </Button>
      </form>
    </Form>
  );
};
