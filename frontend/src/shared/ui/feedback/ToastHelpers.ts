// src/shared/ui/feedback/ToastHelpers.ts
import { ApiError } from '@/shared/lib/api/fetcher';

export function errorToToastDescription(error: unknown): string {
  if (error instanceof ApiError) {
    return `${error.message}${error.code ? ` (${error.code})` : ''}`;
  }
  if (error instanceof Error) return error.message;
  return '不明なエラーが発生しました';
}
