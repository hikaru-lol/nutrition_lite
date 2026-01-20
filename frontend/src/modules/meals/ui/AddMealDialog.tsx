'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, Plus } from 'lucide-react';
import { z } from 'zod';

import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/shared/ui/dialog';
import {
  Form,
  FormControl,
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

import { CreateMealInput, createMealSchema } from '../model/schema';
import { useCreateMeal } from '../hooks/useMeals';

type CreateMealFormValues = z.input<typeof createMealSchema>;

export const AddMealDialog = () => {
  const [open, setOpen] = useState(false);
  const { mutate: create, isPending } = useCreateMeal();

  // 今日の日付をデフォルトに
  const today = new Date().toISOString().split('T')[0];

  const form = useForm<CreateMealFormValues, unknown, CreateMealInput>({
    resolver: zodResolver(createMealSchema),
    defaultValues: {
      date: today,
      meal_type: 'main',
      name: '',
      amount_unit: 'g',
    },
  });

  const onSubmit = (data: CreateMealInput) => {
    create(data, {
      onSuccess: () => {
        setOpen(false);
        form.reset();
      },
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="w-full">
          <Plus className="mr-2 h-4 w-4" />
          食事を追加
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>食事の記録</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>日付</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="meal_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>種類</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="main">メイン</SelectItem>
                        <SelectItem value="snack">間食</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>食品名</FormLabel>
                  <FormControl>
                    <Input placeholder="例: 鶏胸肉のソテー" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="amount_value"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>量</FormLabel>
                    <FormControl>
                      {(() => {
                        const { value, ...rest } = field;
                        return (
                          <Input
                            type="number"
                            step="0.1"
                            placeholder="100"
                            {...rest}
                            value={
                              typeof value === 'string' ||
                              typeof value === 'number'
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
                name="amount_unit"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>単位</FormLabel>
                    <FormControl>
                      <Input placeholder="g" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <Button type="submit" className="w-full" disabled={isPending}>
              {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              保存
            </Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};
