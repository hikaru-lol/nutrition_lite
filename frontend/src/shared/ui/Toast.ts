// src/shared/ui/Toast.ts
import { toast } from 'sonner';

export const Toast = {
  success: (msg: string) => toast.success(msg),
  error: (msg: string) => toast.error(msg),
  info: (msg: string) => toast(msg),
};
