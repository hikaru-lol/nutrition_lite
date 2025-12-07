import type { ReactNode } from 'react';

export default function OnboardingLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex items-center justify-center px-4">
      <div className="w-full max-w-xl">
        <div className="mb-6 text-center">
          <p className="text-xs uppercase tracking-wide text-emerald-400">
            Onboarding
          </p>
          <h1 className="mt-1 text-xl md:text-2xl font-semibold text-slate-50">
            はじめる前に、あなたのことを少し教えてください
          </h1>
          <p className="mt-1 text-xs md:text-sm text-slate-400">
            プロフィールと食事回数を登録すると、よりあなたに合ったターゲットやレポートを生成できます。
          </p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 md:p-6 shadow-lg shadow-slate-950/40">
          {children}
        </div>
      </div>
    </div>
  );
}
