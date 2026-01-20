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
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/shared/ui/form';
// インストールすればここが通ります
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/ui/select';

import { ProfileInput, profileSchema } from '../model/schema';
import { useUpsertProfile } from '../hooks/useProfile';

interface ProfileFormProps {
  onSuccess?: () => void;
}

type ProfileFormValues = z.input<typeof profileSchema>;

export const ProfileForm = ({ onSuccess }: ProfileFormProps) => {
  const { mutate: upsert, isPending } = useUpsertProfile();

  const form = useForm<ProfileFormValues, unknown, ProfileInput>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      birthdate: '',
      meals_per_day: 3,
    },
  });

  const onSubmit = (data: ProfileInput) => {
    upsert(data, {
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
          name="sex"
          render={({ field }) => (
            <FormItem>
              <FormLabel>性別</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="選択してください" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="male">男性</SelectItem>
                  <SelectItem value="female">女性</SelectItem>
                  <SelectItem value="other">その他</SelectItem>
                  <SelectItem value="undisclosed">回答しない</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="birthdate"
          render={({ field }) => (
            <FormItem>
              <FormLabel>生年月日</FormLabel>
              <FormControl>
                <Input type="date" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="height_cm"
            render={({ field }) => (
              <FormItem>
                <FormLabel>身長 (cm)</FormLabel>
                <FormControl>
                  {(() => {
                    const { value, ...rest } = field;
                    return (
                      <Input
                        type="number"
                        step="0.1"
                        placeholder="170.5"
                        {...rest}
                        value={
                          typeof value === 'string' || typeof value === 'number'
                            ? value
                            : ''
                        }
                        onChange={(e) => rest.onChange(e.target.value)}
                      />
                    );
                  })()}
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="weight_kg"
            render={({ field }) => (
              <FormItem>
                <FormLabel>体重 (kg)</FormLabel>
                <FormControl>
                  {(() => {
                    const { value, ...rest } = field;
                    return (
                      <Input
                        type="number"
                        step="0.1"
                        placeholder="60.0"
                        {...rest}
                        value={
                          typeof value === 'string' || typeof value === 'number'
                            ? value
                            : ''
                        }
                        onChange={(e) => rest.onChange(e.target.value)}
                      />
                    );
                  })()}
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <Button type="submit" className="w-full" disabled={isPending}>
          {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          保存して次へ
        </Button>
      </form>
    </Form>
  );
};
