'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2 } from 'lucide-react';
import { z } from 'zod';

import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/shared/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/ui/select';

import { CreateTargetInput, createTargetSchema } from '../model/schema';
import { useCreateTarget } from '../hooks/useTargets';

interface TargetCreationFormProps {
  onSuccess?: () => void;
}

type CreateTargetFormValues = z.input<typeof createTargetSchema>;

export const TargetCreationForm = ({ onSuccess }: TargetCreationFormProps) => {
  const { mutate: create, isPending } = useCreateTarget();

  const form = useForm<CreateTargetFormValues, unknown, CreateTargetInput>({
    resolver: zodResolver(createTargetSchema),
    defaultValues: {
      title: '',
    },
  });

  const onSubmit = (data: CreateTargetInput) => {
    create(data, {
      onSuccess: () => {
        onSuccess?.();
      },
    });
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="w-full space-y-6">
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>目標タイトル</FormLabel>
              <FormControl>
                <Input placeholder="例: 夏までに-3kg" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="goal_type"
          render={({ field }) => (
            <FormItem>
              <FormLabel>目的</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="選択してください" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="weight_loss">減量</SelectItem>
                  <SelectItem value="maintain">現状維持</SelectItem>
                  <SelectItem value="weight_gain">増量</SelectItem>
                  <SelectItem value="health_improve">健康改善</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="activity_level"
          render={({ field }) => (
            <FormItem>
              <FormLabel>普段の活動レベル</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="選択してください" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="low">低い (デスクワーク中心)</SelectItem>
                  <SelectItem value="normal">
                    普通 (立ち仕事・軽い運動)
                  </SelectItem>
                  <SelectItem value="high">
                    高い (肉体労働・激しい運動)
                  </SelectItem>
                </SelectContent>
              </Select>
              <FormDescription>
                これに基づいて推奨カロリーを計算します
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" className="w-full" disabled={isPending}>
          {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          設定を完了して始める
        </Button>
      </form>
    </Form>
  );
};
