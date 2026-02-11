'use client';

import React from 'react';
import { useForm, type SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

import {
  CreateTargetFormSchema,
  createTargetFormDefaultValues,
  goalTypeLabels,
  activityLevelLabels,
  type CreateTargetFormValues,
  type CreateTargetRequest,
} from '../contract/targetContract';

interface CreateTargetModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (values: CreateTargetRequest) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
}

export function CreateTargetModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
  error = null,
}: CreateTargetModalProps) {
  const form = useForm<CreateTargetFormValues>({
    resolver: zodResolver(CreateTargetFormSchema),
    defaultValues: createTargetFormDefaultValues,
  });

  // モーダルが開かれる度にフォームをリセット
  React.useEffect(() => {
    if (isOpen) {
      form.reset(createTargetFormDefaultValues);
    }
  }, [isOpen, form]);

  const handleSubmit: SubmitHandler<CreateTargetFormValues> = async (values) => {
    const req: CreateTargetRequest = {
      title: values.title,
      goal_type: values.goal_type,
      goal_description: values.goal_description || null,
      activity_level: values.activity_level,
    };

    await onSubmit(req);
  };

  const handleClose = () => {
    form.reset();
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>新しいターゲットを作成</DialogTitle>
          <DialogDescription>
            目標に合わせた栄養ターゲットを自動生成します
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
          {/* タイトル */}
          <div className="space-y-2">
            <Label htmlFor="title">タイトル</Label>
            <Input
              id="title"
              placeholder="例: ダイエット2026"
              {...form.register('title')}
              disabled={isLoading}
            />
            {form.formState.errors.title && (
              <p className="text-sm text-destructive">
                {form.formState.errors.title.message}
              </p>
            )}
          </div>

          {/* 目標タイプ */}
          <div className="space-y-2">
            <Label htmlFor="goal_type">目標タイプ</Label>
            <Select
              value={form.watch('goal_type')}
              onValueChange={(v) =>
                form.setValue('goal_type', v as CreateTargetFormValues['goal_type'])
              }
              disabled={isLoading}
            >
              <SelectTrigger>
                <SelectValue placeholder="選択" />
              </SelectTrigger>
              <SelectContent>
                {(
                  Object.keys(goalTypeLabels) as Array<
                    CreateTargetFormValues['goal_type']
                  >
                ).map((key) => (
                  <SelectItem key={key} value={key}>
                    {goalTypeLabels[key]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 活動レベル */}
          <div className="space-y-2">
            <Label htmlFor="activity_level">活動レベル</Label>
            <Select
              value={form.watch('activity_level')}
              onValueChange={(v) =>
                form.setValue(
                  'activity_level',
                  v as CreateTargetFormValues['activity_level']
                )
              }
              disabled={isLoading}
            >
              <SelectTrigger>
                <SelectValue placeholder="選択" />
              </SelectTrigger>
              <SelectContent>
                {(
                  Object.keys(activityLevelLabels) as Array<
                    CreateTargetFormValues['activity_level']
                  >
                ).map((key) => (
                  <SelectItem key={key} value={key}>
                    {activityLevelLabels[key]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 目標の詳細（任意） */}
          <div className="space-y-2">
            <Label htmlFor="goal_description">目標の詳細（任意）</Label>
            <Textarea
              id="goal_description"
              placeholder="例: 3ヶ月で5kg減量したい"
              rows={3}
              {...form.register('goal_description')}
              disabled={isLoading}
            />
          </div>

          {/* エラー表示 */}
          {error && (
            <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md">
              {error}
            </div>
          )}

          {/* アクションボタン */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
            >
              キャンセル
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? '生成中...' : 'ターゲットを生成'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}