import { ReactNode } from 'react';

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    // Rule A: Layoutが「空間（背景・配置）」を定義する
    <div className="flex min-h-screen w-full items-center justify-center bg-gray-50 px-4">
      {/* 家具（Page）を置く場所 */}
      {children}
    </div>
  );
}
